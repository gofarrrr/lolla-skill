#!/usr/bin/env python3
"""Write one schema-owned, owner-only Lolla consumer packet."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.private_runtime import atomic_private_write_json  # noqa: E402
from engine.system_b.run_events import append_run_event  # noqa: E402
from engine.system_b.run_state import (  # noqa: E402
    assert_expected_run_state,
    is_valid_run_id,
)


def _mapping(value: object) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("artifact is not an object")
    return payload


def _readback_packet(extraction: Mapping[str, Any]) -> dict[str, Any]:
    semantic = _mapping(extraction.get("extraction"))
    return {
        "schema_version": "lolla.consumer_packet.readback.v1",
        "stage": "readback",
        "status": extraction.get("status", "missing"),
        "decision_situation": semantic.get("decision_situation", ""),
        "live_constraints": semantic.get("live_constraints", []),
        "synthesized_position": semantic.get("synthesized_position", ""),
        "reasoning_passages": semantic.get("reasoning_passages", []),
        "original_framing": semantic.get("original_framing", ""),
        "dropped_threads": semantic.get("dropped_threads", []),
        "capture_manifest": extraction.get("capture_manifest", {}),
        "capture_adequacy": extraction.get("capture_adequacy", {}),
        "conversation_processing_view": extraction.get(
            "conversation_processing_view", {}
        ),
        "consumer_non_claims": [
            "this_packet_is_a_derivative_processing_view",
            "this_packet_does_not_replace_the_authoritative_conversation",
        ],
    }


def _reconsideration_packet(result: Mapping[str, Any]) -> dict[str, Any]:
    graph = _mapping(result.get("constitutional_graph_survival"))
    v60 = _mapping(result.get("v60_enrichment"))
    private_table = _mapping(result.get("pre_step6_private_table"))
    return {
        "schema_version": "lolla.consumer_packet.reconsideration.v1",
        "stage": "reconsideration",
        "run_health": result.get("run_health", {}),
        "extraction": result.get("extraction", {}),
        "delta_card": result.get("delta_card", {}),
        "companion_cheat_sheet": result.get("companion_cheat_sheet", {}),
        "frame_pressure_card": result.get("frame_pressure_card", {}),
        "structural_coverage_card": result.get("structural_coverage_card", {}),
        "bullshit_profile": result.get("bullshit_profile", {}),
        "constitutional_graph_survival": {
            "status": graph.get("status", "missing"),
            "active_pressure_items": graph.get("active_pressure_items", []),
            "disposition_ledger_skeleton": graph.get(
                "disposition_ledger_skeleton", {}
            ),
            "selection_contract": graph.get("selection_contract", {}),
            "non_claims": graph.get("non_claims", []),
        },
        "pre_step6_private_table": {
            "status": private_table.get("status", "missing"),
            "source_items": private_table.get("source_items", []),
            "consideration_ledger_skeleton": private_table.get(
                "consideration_ledger_skeleton", {}
            ),
            "consumer_material": private_table.get("consumer_material", {}),
            "gates": private_table.get("gates", {}),
        },
        "v60_enrichment": {
            "status": v60.get("status", "missing"),
            "selected_cards": v60.get("selected_cards", []),
            "consideration_ledger_skeleton": v60.get(
                "consideration_ledger_skeleton", {}
            ),
            "telemetry": v60.get("telemetry", {}),
        },
        "consumer_non_claims": [
            "graph_admission_is_not_relevance_proof",
            "selected_pressure_is_not_a_command",
            "the_reasoner_may_apply_reject_or_park_pressure",
        ],
    }


def _verification_packet(result: Mapping[str, Any]) -> dict[str, Any]:
    run_health = _mapping(result.get("run_health"))
    usage = _mapping(result.get("usage_summary"))
    extraction = _mapping(result.get("extraction"))
    graph = _mapping(result.get("constitutional_graph_survival"))
    return {
        "schema_version": "lolla.consumer_packet.verification.v1",
        "stage": "verification",
        "run_health": {
            "overall": run_health.get("overall", "unknown"),
            "issues": run_health.get("issues", []),
            "capture": run_health.get("capture", "unknown"),
            "source_coverage": run_health.get("source_coverage", {}),
            "constitutional_graph_survival_ledger": run_health.get(
                "constitutional_graph_survival_ledger", "unknown"
            ),
            "pre_step6_private_table_ledger": run_health.get(
                "pre_step6_private_table_ledger", "unknown"
            ),
            "v60_consideration_ledger": run_health.get(
                "v60_consideration_ledger", "unknown"
            ),
            "live_output_health": run_health.get(
                "live_output_health", "not_checked"
            ),
            "complete_visible_surface_observed": run_health.get(
                "complete_visible_surface_observed", False
            ),
            "complete_visible_surface_leak_count": run_health.get(
                "complete_visible_surface_leak_count"
            ),
        },
        "source": {
            "capture_manifest": result.get("capture_manifest")
            or extraction.get("capture_manifest")
            or {},
            "capture_adequacy": result.get("capture_adequacy")
            or extraction.get("capture_adequacy")
            or {},
            "conversation_processing_view": result.get(
                "conversation_processing_view"
            )
            or extraction.get("conversation_processing_view")
            or {},
        },
        "graph": {
            "status": graph.get("status", "missing"),
            "path_counts": graph.get("path_counts", {}),
            "selection_contract": graph.get("selection_contract", {}),
            "ledger_validation": result.get(
                "constitutional_graph_survival_ledger_validation", {}
            ),
        },
        "private_table_validation": result.get(
            "pre_step6_private_table_ledger_validation", {}
        ),
        "v60_validation": result.get("v60_consideration_validation", {}),
        "usage": {
            "estimated_total_cost_usd": usage.get("estimated_total_cost_usd"),
            "cost_estimate_state": usage.get("cost_estimate_state", "unknown"),
            "provider_budget_enforcement_scope": usage.get(
                "provider_budget_enforcement_scope",
                {"status": "not_declared_by_legacy_result"},
            ),
        },
        "consumer_non_claims": [
            "structural_validation_is_not_semantic_correctness",
            "clean_curated_narration_is_not_complete_host_surface_proof",
            "run_health_is_not_a_quality_score",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--stage",
        required=True,
        choices=("readback", "reconsideration", "verification"),
    )
    parser.add_argument("--tmp-dir", default=os.getenv("LOLLA_TMP_DIR", "/tmp"))
    args = parser.parse_args()

    run_id = str(args.run_id).strip()
    if not is_valid_run_id(run_id):
        print("CONSUMER_PACKET_STATUS: invalid_run", file=sys.stderr)
        return 2
    try:
        assert_expected_run_state(
            actual_run_id=run_id,
            phase=f"prepare_consumer_packet_{args.stage}",
        )
    except SystemExit:
        print("CONSUMER_PACKET_STATUS: run_mismatch", file=sys.stderr)
        return 2

    tmp_dir = Path(args.tmp_dir).expanduser()
    try:
        if args.stage == "readback":
            source = _read_json(tmp_dir / f"lolla_{run_id}_extraction.json")
            packet = _readback_packet(source)
        else:
            source = _read_json(tmp_dir / f"lolla_{run_id}_result.json")
            packet = (
                _reconsideration_packet(source)
                if args.stage == "reconsideration"
                else _verification_packet(source)
            )
    except (OSError, ValueError, json.JSONDecodeError):
        print(
            f"CONSUMER_PACKET_STATUS: {args.stage} unavailable",
            file=sys.stderr,
        )
        return 2

    output = tmp_dir / f"lolla_{run_id}_consumer_{args.stage}.json"
    try:
        atomic_private_write_json(output, packet)
    except Exception:
        print(
            f"CONSUMER_PACKET_STATUS: {args.stage} unavailable",
            file=sys.stderr,
        )
        return 2

    events_path = tmp_dir / f"lolla_{run_id}_run_events.json"
    try:
        append_run_event(
            run_id=run_id,
            event_type="consumer_packet_prepared",
            actor="skill",
            path=events_path,
            details={
                "stage": args.stage,
                "source_projection": True,
                "complete_host_tool_stream_captured": False,
            },
        )
        events_path.chmod(0o600)
    except Exception:
        print(
            f"CONSUMER_PACKET_STATUS: {args.stage} incomplete; "
            "packet=written; event_custody=failed",
            file=sys.stderr,
        )
        return 2
    print(f"CONSUMER_PACKET_STATUS: {args.stage} ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
