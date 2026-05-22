from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_lens_answer_cores import validate_lens_answer_core_payload  # noqa: E402
from pre_step6_lens_comparisons import (  # noqa: E402
    score_lens_comparison,
    validate_lens_comparison_payload,
)
from pre_step6_lens_probes import validate_lens_probe_payload  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]
PROBE_DIR = REPO_ROOT / "research/pre-step6-lens-probes"
ANSWER_DIR = REPO_ROOT / "research/pre-step6-lens-answer-cores"
COMPARISON_DIR = REPO_ROOT / "research/pre-step6-lens-comparisons"


def test_polya_lens_probe_answer_and_comparison_fixtures_validate_fixed_suite() -> None:
    probe_paths = sorted(PROBE_DIR.glob("*.polya-lens-probe.v1.json"))
    answer_paths = sorted(ANSWER_DIR.glob("*.polya-answer-core.v1.json"))
    comparison_paths = sorted(COMPARISON_DIR.glob("*.polya-comparison.v1.json"))

    expected_names = {
        "founder-grant-marcus-equity.high-clutter",
        "mid-level-consultant-report-2",
        "mother-address-year",
        "third-year-phd-student.v2",
    }
    assert {path.name.removesuffix(".polya-lens-probe.v1.json") for path in probe_paths} == expected_names
    assert {path.name.removesuffix(".polya-answer-core.v1.json") for path in answer_paths} == expected_names
    assert {path.name.removesuffix(".polya-comparison.v1.json") for path in comparison_paths} == expected_names

    for path in probe_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_lens_probe_payload(payload, path=path)
        assert payload["lens_pack"] == "polya_problem_solving_v0"

    for path in answer_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_lens_answer_core_payload(payload, path=path, repo_root=REPO_ROOT)
        assert payload["lens_pack"] == "polya_problem_solving_v0"
        assert "polya" not in payload["answer_core"].lower()

    expected_decisions = {
        "founder-grant-marcus-equity.high-clutter.polya-comparison.v1.json": "lens_boundary_case",
        "mid-level-consultant-report-2.polya-comparison.v1.json": "lens_boundary_case",
        "mother-address-year.polya-comparison.v1.json": "lens_boundary_case",
        "third-year-phd-student.v2.polya-comparison.v1.json": "lens_improves",
    }
    for path in comparison_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_lens_comparison_payload(payload, path=path, repo_root=REPO_ROOT)
        score = score_lens_comparison(payload)
        assert score["aggregate_decision"] == payload["aggregate_decision"]
        assert payload["aggregate_decision"] == expected_decisions[path.name]
