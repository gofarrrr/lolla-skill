#!/usr/bin/env python3
"""Seal provider-free role joins from preserved Gemini Lite artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from engine.system_b.reasoning_process_qualification_detail_v1 import (
    materialize_quiet_qualification_role_v1,
)
from engine.system_b.reasoning_process_qualification_review_v1 import (
    join_decomposed_current_qualification_v1,
)
from engine.system_b.simulated_reliability_v1 import join_role_records_v1


ROOT = Path(__file__).resolve().parents[2]


def _load(path: str) -> dict[str, Any]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build(output: Path) -> dict[str, Any]:
    case06_starting = _load(
        "research/simulated-reliability-v1-model-value-probe-2026-07-13/a1/"
        "gemini-3-1-flash-lite-vertex-starting/call-01-starting-result.json"
    )["compiled"]
    case06_roles = _load(
        "research/simulated-reliability-v1-lite-decomposed-roles-2026-07-13/a1/result.json"
    )["roles"]
    case06_current = next(row["compiled"] for row in case06_roles if row["role"] == "current")
    case06_review = _load(
        "research/simulated-reliability-v1-lite-qualification-review-2026-07-13/a1/"
        "v1-case06-industry-funded-lab/call-01-qualification_review-result.json"
    )["compiled"]
    case06_qualification = _load(
        "research/simulated-reliability-v1-lite-qualification-detail-2026-07-13/a1/result.json"
    )["compiled"]
    case06_paired = join_decomposed_current_qualification_v1(
        current_compiled=case06_current,
        qualification_compiled=case06_qualification,
        qualification_review=case06_review,
    )
    case06_portfolio = join_role_records_v1(
        starting_compiled=case06_starting,
        paired_compiled=case06_paired,
    )

    case07_roles = _load(
        "research/simulated-reliability-v1-lite-decomposed-roles-quiet-2026-07-13/a1/result.json"
    )["roles"]
    case07_current = next(row["compiled"] for row in case07_roles if row["role"] == "current")
    case07_review = _load(
        "research/simulated-reliability-v1-lite-qualification-review-2026-07-13/a1/"
        "v1-case07-cooperative-scheduling/call-02-qualification_review-result.json"
    )["compiled"]
    case07_wrapper = _load(
        "research/simulated-reliability-corpus-v1-2026-07-12/"
        "provider-free-role-input-preflight/transfer/"
        "v1-case07-cooperative-scheduling/position-wrapper.json"
    )
    case07_quiet = materialize_quiet_qualification_role_v1(
        wrapper=case07_wrapper,
        review=case07_review,
    )
    case07_paired = join_decomposed_current_qualification_v1(
        current_compiled=case07_current,
        qualification_compiled=case07_quiet,
        qualification_review=case07_review,
    )

    output.mkdir(parents=True, exist_ok=False)
    _write(output / "case06-paired.json", case06_paired)
    _write(output / "case06-role-portfolio.json", case06_portfolio)
    _write(output / "case07-paired.json", case07_paired)
    report = {
        "schema_version": "lolla.simulated_reliability_lite_role_joins_result.v1",
        "status": "provider_free_joins_complete",
        "case06": {
            "paired_join": "complete",
            "full_role_portfolio": "complete",
            "record_counts": case06_portfolio["record_counts"],
            "qualification_review_outcome": case06_review["outcome"],
        },
        "case07": {
            "paired_join": "complete",
            "full_role_portfolio": "not_attempted_lite_starting_not_available",
            "current_observation_count": len(case07_current["observations"]),
            "qualification_observation_count": len(case07_quiet["observations"]),
            "qualification_review_outcome": case07_review["outcome"],
        },
        "provider_calls": 0,
        "semantic_repair_performed": False,
        "deterministic_semantic_inference": False,
        "quiet_false_positive_used_in_join": False,
        "production_model_selected": False,
        "scalar_quality_score": None,
    }
    _write(output / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise RuntimeError("role-join output path must not exist")
    report = build(output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
