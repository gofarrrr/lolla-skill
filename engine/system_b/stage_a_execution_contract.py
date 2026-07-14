"""Shared deterministic field contract for Stage A execution envelopes."""
from __future__ import annotations

from collections.abc import Mapping


RUN_DIRECTORY_ABSENT_GATE = "run_directory_absent_before_run"
SIDECARS_ABSENT_GATE = "all_sidecars_absent_before_run"
EXTRACTION_EXIT_ZERO_GATE = "extraction_exit_zero"
EXTRACTION_TIMEOUT_CLEAR_GATE = "extraction_outer_timeout_not_triggered"
PIPELINE_EXIT_ZERO_GATE = "pipeline_exit_zero"
PIPELINE_TIMEOUT_CLEAR_GATE = "pipeline_outer_timeout_not_triggered"

REQUIRED_EXECUTION_GATE_FIELDS = frozenset(
    {
        RUN_DIRECTORY_ABSENT_GATE,
        SIDECARS_ABSENT_GATE,
        EXTRACTION_EXIT_ZERO_GATE,
        EXTRACTION_TIMEOUT_CLEAR_GATE,
        PIPELINE_EXIT_ZERO_GATE,
        PIPELINE_TIMEOUT_CLEAR_GATE,
    }
)


def validate_stage_a_execution_gates(gates: Mapping[str, object]) -> None:
    """Reject runner/sealer field drift before an envelope is persisted or read."""
    missing = sorted(REQUIRED_EXECUTION_GATE_FIELDS - set(gates))
    if missing:
        raise ValueError(f"Stage A execution gates missing canonical fields: {missing}")
    if "extractor_exit_zero" in gates:
        raise ValueError(
            "legacy extractor_exit_zero is forbidden; use extraction_exit_zero"
        )
    non_boolean = sorted(
        name for name in REQUIRED_EXECUTION_GATE_FIELDS if not isinstance(gates[name], bool)
    )
    if non_boolean:
        raise ValueError(
            f"Stage A execution gates must be booleans: {non_boolean}"
        )
