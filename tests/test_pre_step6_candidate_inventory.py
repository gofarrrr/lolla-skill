from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_build_candidate_inventory import (  # noqa: E402
    build_candidate_inventory,
    validate_candidate_inventory_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
MARCUS_DIR = REPO_ROOT / "research/test-cases/phase2d-marcus-controlled-comparison-2026-04-24"
RAW_DIR = REPO_ROOT / "research/pre-step6-raw-artifact-fixtures"
HYBRID_DIR = REPO_ROOT / "research/pre-step6-hybrid-handoff-fixtures"
FIXTURE_DIR = REPO_ROOT / "research/pre-step6-candidate-inventories"


def test_marcus_result_produces_candidates_for_engineered_artifacts() -> None:
    payload = build_candidate_inventory(
        case_id="marcus_new_path_result",
        result_file=MARCUS_DIR / "marcus_new_path_result.json",
    )

    validate_candidate_inventory_payload(payload)
    origins = {candidate["origin"] for candidate in payload["candidates"]}
    assert {
        "delta_card",
        "companion_card",
        "frame_pressure_card",
        "structural_coverage_card",
        "audit_summary",
        "run_health",
    }.issubset(origins)


def test_inventory_preserves_raw_and_hybrid_expansion_refs() -> None:
    payload = build_candidate_inventory(
        case_id="founder-grant-marcus-equity.high-clutter",
        raw_handoff_files=[RAW_DIR / "founder-grant-marcus-equity.raw-artifact-handoff.v1.json"],
        hybrid_handoff_files=[
            HYBRID_DIR / "founder-grant-marcus-equity.high-clutter.hybrid-handoff.v1.json"
        ],
    )

    validate_candidate_inventory_payload(payload)
    candidates = payload["candidates"]
    raw_candidate = next(
        candidate
        for candidate in candidates
        if candidate["candidate_id"] == "founder_duplicate_valuation_base_rate_gate"
    )
    hybrid_candidate = next(
        candidate
        for candidate in candidates
        if candidate["origin"] == "hybrid_inspect_more"
    )

    assert raw_candidate["origin"] == "raw_artifact_handoff"
    assert raw_candidate["source_refs"]
    assert raw_candidate["expansion_ref"]
    assert hybrid_candidate["source_refs"]
    assert hybrid_candidate["expansion_ref"]


def test_static_candidate_inventory_fixtures_validate() -> None:
    paths = sorted(FIXTURE_DIR.glob("*.candidate-inventory.v1.json"))

    assert [path.name for path in paths] == [
        "marcus_new_path_result.candidate-inventory.v1.json",
        "mid-level-consultant-report-2.candidate-inventory.v1.json",
        "mother-address-year.candidate-inventory.v1.json",
        "third-year-phd-student.candidate-inventory.v1.json",
    ]
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_candidate_inventory_payload(payload, path=path)
