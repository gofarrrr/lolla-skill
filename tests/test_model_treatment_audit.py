from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "observatory"))

import serve_result  # noqa: E402
from system_b.model_treatment_audit import (  # noqa: E402
    ModelTreatmentAuditValidationError,
    build_summary_payload,
    selected_models_by_lane,
    validate_treatment_audit_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / "data" / "treatment_audits"


def _audit_paths() -> list[Path]:
    return sorted(
        path for path in AUDIT_DIR.glob("*__*.json") if not path.name.endswith(".v1.json")
    )


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_committed_treatment_audits_validate_quotes_and_shape() -> None:
    paths = _audit_paths()
    assert len(paths) == 5

    for path in paths:
        payload = _load(path)
        validate_treatment_audit_payload(payload)
        for item in payload["items"]:
            quote = item["output_quote"]
            if quote:
                assert quote in item["audited_output_slice"]


def test_treatment_audit_summary_matches_committed_runs() -> None:
    audits = [_load(path) for path in _audit_paths()]
    summary = _load(AUDIT_DIR / "summary.json")
    recomputed = build_summary_payload(audits)

    assert summary["audited_run_count"] == 5
    assert summary["audited_item_count"] == sum(len(audit["items"]) for audit in audits)
    assert summary["new_finding_count"] == len(summary["new_findings"])
    assert summary["judge_rejection_count"] == recomputed["judge_rejection_count"]
    assert summary["treatment_status_distribution"] == recomputed["treatment_status_distribution"]
    assert summary["baseline_coverage_distribution"] == recomputed["baseline_coverage_distribution"]
    assert summary["activation_status_distribution"] == recomputed["activation_status_distribution"]
    assert summary["evidence_tier_distribution"] == recomputed["evidence_tier_distribution"]
    assert summary["metadata"]["judge_provider"] == "openrouter"
    assert summary["metadata"]["judge_model"]
    assert summary["token_usage"]["total_tokens"] > 0


def test_do_not_promote_items_are_excluded_from_merge_gate_count() -> None:
    flagged = []
    for path in _audit_paths():
        payload = _load(path)
        flagged.extend(
            item
            for item in payload["items"]
            if item["do_not_promote_without_rewrite_review"]
        )

    assert flagged
    assert all(not item["merge_gate_evidence_candidate"] for item in flagged)


def test_validator_rejects_non_exact_output_quote() -> None:
    payload = _load(_audit_paths()[0])
    broken = copy.deepcopy(payload)
    broken["items"][0]["output_quote"] = "This is a paraphrase, not a copied quote."

    with pytest.raises(ModelTreatmentAuditValidationError, match="exact substring"):
        validate_treatment_audit_payload(broken)


def test_validator_rejects_short_treated_quote() -> None:
    payload = _load(_audit_paths()[0])
    broken = copy.deepcopy(payload)
    broken["items"][0]["treatment_status"] = "treated"
    broken["items"][0]["output_quote"] = broken["items"][0]["audited_output_slice"][:10]

    with pytest.raises(ModelTreatmentAuditValidationError, match="shorter than"):
        validate_treatment_audit_payload(broken)


def test_selected_models_by_lane_extracts_all_lane_sources() -> None:
    trace = {
        "lanes": {
            "lane1": {"routes": [{"selected_model_ids": ["base-rates", "premortem"]}]},
            "lane2": {"selected_model_ids": ["base-rates", "empathy"]},
            "lane3": {"routes": [{"selected_model_ids": ["inversion"]}]},
            "lane4": {"routes": [{"selected_model_ids": ["opportunity-cost", "premortem"]}]},
        }
    }

    assert selected_models_by_lane(trace) == {
        "base-rates": ["lane1", "lane2"],
        "empathy": ["lane2"],
        "inversion": ["lane3"],
        "opportunity-cost": ["lane4"],
        "premortem": ["lane1", "lane4"],
    }


def test_observatory_treatment_audit_pages_render() -> None:
    summary_html = serve_result._render_treatment_audit_index_html()
    assert "Model Treatment Audit" in summary_html
    assert "Merge-Gate Candidate Findings" in summary_html
    assert "coverage-style" not in summary_html.lower()

    run_id = _audit_paths()[0].stem
    detail_html = serve_result._render_treatment_audit_run_html(run_id)
    assert "Per-Affordance Treatment" in detail_html
    assert "Pressure Check Baseline" in detail_html
    assert "do-not-promote" in detail_html or "merge-gate candidate" in detail_html
