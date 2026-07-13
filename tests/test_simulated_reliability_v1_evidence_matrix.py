from __future__ import annotations

import hashlib
from pathlib import Path

from scripts.evals.build_simulated_reliability_v1_evidence_matrix import ROOT, build


def test_evidence_matrix_reconciles_usage_and_never_collapses_to_score() -> None:
    report = build()
    assert report["usage"]["calibration"]["attempted_calls"] == 62
    assert report["usage"]["calibration"]["operationally_ok"] == 57
    assert report["usage"]["transfer"]["attempted_calls"] == 34
    assert report["usage"]["transfer"]["operationally_ok"] == 30
    assert report["usage"]["total"]["attempted_calls"] == 96
    assert report["usage"]["total"]["operationally_ok"] == 87
    assert report["usage"]["total"]["provider_reported_cost_usd"] == 3.1495905
    assert report["single_quality_score"] is None


def test_evidence_matrix_keeps_incomplete_requirements_open() -> None:
    report = build()
    rows = {row["requirement_id"]: row for row in report["requirements"]}
    assert rows["integrity"]["status"] == "supported"
    assert rows["restraint"]["status"] == "mixed"
    assert rows["usefulness"]["status"] == "not_established"
    assert rows["graph_attribution"]["status"] == "calibration_only"
    assert rows["stability"]["status"] == "not_yet_measured"
    assert rows["receipt_reconstruction"]["status"] == "not_yet_measured"
    assert report["current_decision"]["v1_reliability_evaluation_complete"] is False
    assert report["current_decision"]["additional_provider_calls_authorized"] == 0


def test_every_evidence_lock_matches_current_bytes() -> None:
    report = build()
    for row in report["evidence_locks"]:
        path = ROOT / row["path"]
        assert path.is_file()
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
