from __future__ import annotations

from pathlib import Path
from typing import Any

from system_b.decision_pressure_trace_validation import (
    load_decision_pressure_trace_payload,
    validate_decision_pressure_trace_payload,
)


ADAPTER_POLICY = "fixture_only_review_report"


def build_decision_pressure_trace_review_report(
    *,
    fixture_path: Path,
    compiled_affordances_path: Path,
) -> dict[str, object]:
    payload = load_decision_pressure_trace_payload(Path(fixture_path))
    validate_decision_pressure_trace_payload(
        payload,
        path=Path(fixture_path),
        compiled_affordances_path=Path(compiled_affordances_path),
    )

    selected_pressures = _list(payload.get("selected_pressures"))
    coverage_panels = _list(payload.get("coverage_transparency_panels"))
    suppressed_candidates = _list(payload.get("suppressed_candidates"))
    review_notes = _dict(payload.get("review_notes"))
    source_affordance_ids = sorted(
        {
            str(affordance_id)
            for pressure in selected_pressures
            for affordance_id in _list(_dict(pressure).get("source_affordances"))
        }
    )

    return {
        "schema_version": str(payload.get("schema_version")),
        "trace_id": str(payload.get("trace_id")),
        "status": str(payload.get("status")),
        "runtime_policy": str(payload.get("runtime_policy")),
        "selected_pressure_count": len(selected_pressures),
        "coverage_transparency_panel_count": len(coverage_panels),
        "suppressed_candidate_count": len(suppressed_candidates),
        "selected_pressure_ids": [
            str(_dict(pressure).get("pressure_id")) for pressure in selected_pressures
        ],
        "coverage_panel_ids": [
            str(_dict(panel).get("panel_id")) for panel in coverage_panels
        ],
        "suppressed_candidate_ids": [
            str(_dict(candidate).get("candidate_id"))
            for candidate in suppressed_candidates
        ],
        "source_affordance_count": sum(
            len(_list(_dict(pressure).get("source_affordances")))
            for pressure in selected_pressures
        ),
        "unique_source_affordance_ids": source_affordance_ids,
        "blocked_surfaces": [
            str(surface) for surface in _list(review_notes.get("blocked_surfaces"))
        ],
        "validation_status": "passed",
        "adapter_policy": ADAPTER_POLICY,
    }


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []
