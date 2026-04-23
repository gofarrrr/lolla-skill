"""Tests for scripts/compare_outputs.py."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.compare_outputs import compare_results, render_report


def _base_payload() -> dict:
    return {
        "detected_tendencies": ["doubt-avoidance-tendency"],
        "delta_card": {
            "findings": [{"tendency_id": "doubt-avoidance-tendency", "severity": "medium"}],
        },
        "companion_cheat_sheet": {
            "anchors": [{"model_id": "first-principles-thinking"}],
        },
        "frame_pressure_card": {
            "reframings": [{"reframed_question": "Should I, really?"}],
        },
        "structural_coverage_card": {
            "gap_questions": [{"question": "Who pays when it fails?"}],
        },
        "audit_summary": {
            "triggered_tendencies": ["doubt-avoidance-tendency"],
            "boundary_call_count": 17,       # should be ignored — not in the compare set
            "pass1_seconds": 1.23,           # should be ignored — timing
        },
        "run_health": {"quote_fabrication": 0},
    }


def test_identical_payloads_all_match() -> None:
    left = _base_payload()
    right = _base_payload()
    report = compare_results(left, right)
    assert report.all_match is True
    for f in report.fields:
        assert f.match, f"{f.field_name} reported mismatch on identical payloads"


def test_mismatch_on_detected_tendencies() -> None:
    left = _base_payload()
    right = _base_payload()
    right["detected_tendencies"] = ["overoptimism-tendency"]
    report = compare_results(left, right)
    assert report.all_match is False
    mismatched = {f.field_name for f in report.mismatches}
    assert mismatched == {"detected_tendencies"}
    # Other meaningful fields still match
    others = [f for f in report.fields if f.field_name != "detected_tendencies"]
    assert all(f.match for f in others)


def test_mismatch_on_delta_card_findings() -> None:
    left = _base_payload()
    right = _base_payload()
    right["delta_card"]["findings"][0]["severity"] = "high"
    report = compare_results(left, right)
    assert report.all_match is False
    mismatched = {f.field_name for f in report.mismatches}
    assert mismatched == {"delta_card.findings"}


def test_timing_differences_are_ignored() -> None:
    """boundary_call_count and *_seconds fields differ → still 'all match'."""
    left = _base_payload()
    right = _base_payload()
    right["audit_summary"]["boundary_call_count"] = 999
    right["audit_summary"]["pass1_seconds"] = 4.56
    report = compare_results(left, right)
    assert report.all_match is True, (
        "Timing/boundary metadata must be ignored; only the 6 meaningful fields count."
    )


def test_missing_lane_cards_treated_as_empty() -> None:
    """A None card must compare equal to a None card; empty list on one side
    to an absent card on the other should also match."""
    left = _base_payload()
    left["frame_pressure_card"] = None
    right = _base_payload()
    right["frame_pressure_card"] = None
    report = compare_results(left, right)
    assert report.all_match is True


def test_render_report_labels_match_and_diverge() -> None:
    left = _base_payload()
    right = _base_payload()
    right["detected_tendencies"] = ["other"]
    output = render_report(compare_results(left, right), left_label="old", right_label="new")
    assert "MATCH" in output
    assert "DIFFER" in output
    assert "detected_tendencies" in output
    assert "old" in output and "new" in output


def test_main_exit_codes(tmp_path: Path) -> None:
    import subprocess

    left = tmp_path / "left.json"
    right = tmp_path / "right.json"
    import json
    left.write_text(json.dumps(_base_payload()))
    right.write_text(json.dumps(_base_payload()))

    repo_root = Path(__file__).resolve().parents[1]

    ok = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "compare_outputs.py"), str(left), str(right)],
        capture_output=True,
    )
    assert ok.returncode == 0
    assert b"all 6 meaningful fields match" in ok.stdout

    # Divergent case
    divergent = _base_payload()
    divergent["detected_tendencies"] = ["different"]
    right.write_text(json.dumps(divergent))

    bad = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "compare_outputs.py"), str(left), str(right)],
        capture_output=True,
    )
    assert bad.returncode == 1
    assert b"fields diverge" in bad.stdout
