#!/usr/bin/env python3
"""Research-only validation for Step 6 portfolio comparison readouts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Sequence


PORTFOLIO_COMPARISON_SCHEMA_VERSION = "pre_step6_portfolio_comparison.v1"
ALLOWED_STATUS = frozenset({"research_only"})
ALLOWED_RUNTIME_POLICY = frozenset({"runtime_dormant"})
ALLOWED_MODE_IDS = frozenset({"A", "B", "C", "D", "E", "F", "unavailable"})
ALLOWED_PRUNING_RISK = frozenset({"low", "medium", "high", "unknown"})
ALLOWED_JUDGMENTS = frozenset(
    {
        "portfolio_wins",
        "portfolio_promising",
        "raw_or_hybrid_wins",
        "tie_keep_research_only",
        "negative_control_success",
    }
)
TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_refs",
        "modes",
        "metrics",
        "aggregate_judgment",
        "falsifiers",
        "recommendation",
        "notes",
    }
)
MODE_FIELDS = frozenset(
    {
        "mode_id",
        "label",
        "source_ref",
        "render_chars",
        "active_count",
        "edge_count",
        "parked_count",
        "source_ref_count",
        "premature_pruning_risk",
        "answer_usefulness_judgment",
    }
)
METRICS_FIELDS = frozenset(
    {
        "latency_proxy",
        "token_cost_proxy",
        "edge_pressure_preservation",
        "artifact_bloat",
        "negative_control_behavior",
    }
)


class PortfolioComparisonValidationError(ValueError):
    pass


def load_portfolio_comparison_payload(path: Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PortfolioComparisonValidationError(f"{path}: payload must be an object")
    return payload


def validate_portfolio_comparison_payload(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_portfolio_comparison_errors(payload, path=Path(path)))
    if errors:
        raise PortfolioComparisonValidationError("; ".join(errors))


def validate_portfolio_comparison_file(path: Path) -> None:
    validate_portfolio_comparison_payload(
        load_portfolio_comparison_payload(path),
        path=Path(path),
    )


def iter_portfolio_comparison_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = (
        "schema_version",
        "status",
        "runtime_policy",
        "case_id",
        "source_refs",
        "modes",
        "metrics",
        "aggregate_judgment",
        "falsifiers",
        "recommendation",
    )
    yield from _unknown_fields(payload, TOP_LEVEL_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if _string(payload.get("schema_version")) != PORTFOLIO_COMPARISON_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {PORTFOLIO_COMPARISON_SCHEMA_VERSION}"
    if _string(payload.get("status")) not in ALLOWED_STATUS:
        yield f"{path / 'status'}: status must be research_only"
    if _string(payload.get("runtime_policy")) not in ALLOWED_RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: runtime_policy must be runtime_dormant"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: case_id must be non-empty"
    if not _non_empty_string_list(payload.get("source_refs")):
        yield f"{path / 'source_refs'}: source_refs must be a non-empty string list"
    if _string(payload.get("aggregate_judgment")) not in ALLOWED_JUDGMENTS:
        yield f"{path / 'aggregate_judgment'}: unknown aggregate_judgment"
    if not _non_empty_string_list(payload.get("falsifiers")):
        yield f"{path / 'falsifiers'}: falsifiers must be a non-empty string list"
    if not _string(payload.get("recommendation")).strip():
        yield f"{path / 'recommendation'}: recommendation must be non-empty"
    yield from _validate_modes(payload.get("modes"), path / "modes")
    yield from _validate_metrics(payload.get("metrics"), path / "metrics")


def _validate_modes(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list) or not value:
        yield f"{path}: modes must be a non-empty list"
        return
    for index, mode in enumerate(value):
        item_path = path / f"[{index}]"
        if not isinstance(mode, dict):
            yield f"{item_path}: mode must be an object"
            continue
        yield from _unknown_fields(mode, MODE_FIELDS, item_path)
        yield from _missing_fields(mode, tuple(MODE_FIELDS), item_path)
        if any(field not in mode for field in MODE_FIELDS):
            continue
        if _string(mode.get("mode_id")) not in ALLOWED_MODE_IDS:
            yield f"{item_path / 'mode_id'}: unknown mode_id"
        if _string(mode.get("premature_pruning_risk")) not in ALLOWED_PRUNING_RISK:
            yield f"{item_path / 'premature_pruning_risk'}: unknown premature_pruning_risk"
        for field in ("label", "source_ref", "answer_usefulness_judgment"):
            if not _string(mode.get(field)).strip():
                yield f"{item_path / field}: must be non-empty"
        for field in (
            "render_chars",
            "active_count",
            "edge_count",
            "parked_count",
            "source_ref_count",
        ):
            if not isinstance(mode.get(field), int) or mode.get(field) < 0:
                yield f"{item_path / field}: must be a non-negative integer"


def _validate_metrics(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: metrics must be an object"
        return
    yield from _unknown_fields(value, METRICS_FIELDS, path)
    yield from _missing_fields(value, tuple(METRICS_FIELDS), path)
    if any(field not in value for field in METRICS_FIELDS):
        return
    for field in METRICS_FIELDS:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"


def _unknown_fields(
    payload: dict[str, object],
    allowed: frozenset[str],
    path: Path,
) -> Iterable[str]:
    for field in sorted(set(payload) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(
    payload: dict[str, object],
    required: Sequence[str],
    path: Path,
) -> Iterable[str]:
    for field in required:
        if field not in payload:
            yield f"{path / field}: missing required field"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _non_empty_string_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(argv)
    for path in args.paths:
        validate_portfolio_comparison_file(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
