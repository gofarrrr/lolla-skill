from __future__ import annotations

import json
from pathlib import Path

from scripts.run_v60_source_ablation_analysis import analyze, classify_sources


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_classify_sources_separates_strict_lane_and_enhanced() -> None:
    assert classify_sources(["lane_preserved"]) == "strict_lane"
    assert classify_sources(["embedding_absence_exact"]) == "embedding_absence"
    assert classify_sources(["embedding_affordance_exact"]) == "embedding_affordance"
    assert classify_sources(["hybrid_rrf_exact"]) == "hybrid_rrf"
    assert (
        classify_sources(["embedding_affordance_exact", "lane_preserved"])
        == "mixed_lane_enhanced"
    )


def test_analyze_counts_safe_enhanced_delta_and_unsafe_lane_delta(tmp_path: Path) -> None:
    profile_a = {
        "composer_opportunities": [
            {
                "opportunity_id": "lane-risk",
                "route": "public_delta_candidate",
                "source_mix": ["lane_preserved"],
                "model_ids": ["margin-of-safety"],
                "private_value": "Sharpen buffer.",
            }
        ]
    }
    output_a = {
        "admitted_items": [
            {
                "source_opportunity_ids": ["lane-risk"],
                "public_delta": "Add a made-up 24K buffer miss.",
            }
        ]
    }
    profile_b = {
        "composer_opportunities": [
            {
                "opportunity_id": "embed-option",
                "route": "public_delta_candidate",
                "source_mix": ["embedding_affordance_exact"],
                "model_ids": ["optionality"],
                "private_value": "Add a hybrid option.",
            }
        ]
    }
    output_b = {
        "admitted_items": [
            {
                "source_opportunity_ids": ["embed-option"],
                "public_delta": "Consider a hybrid option.",
            }
        ]
    }
    _write_json(tmp_path / "system_profiles" / "a.json", profile_a)
    _write_json(tmp_path / "composer_outputs" / "a.json", output_a)
    _write_json(tmp_path / "system_profiles" / "b.json", profile_b)
    _write_json(tmp_path / "composer_outputs" / "b.json", output_b)
    c45_summary = {
        "items": [
            {
                "case_id": "a",
                "system_profile_path": "system_profiles/a.json",
                "composer_output_path": "composer_outputs/a.json",
                "composer_validation": {
                    "status": "invalid",
                    "admission_decision": "mixed",
                    "errors": ["numeric novelty"],
                },
            },
            {
                "case_id": "b",
                "system_profile_path": "system_profiles/b.json",
                "composer_output_path": "composer_outputs/b.json",
                "composer_validation": {
                    "status": "valid",
                    "admission_decision": "admit_delta",
                },
            },
        ],
        "aggregate": {"call_count": 2, "cost_usd": 0.01},
    }

    result = analyze(
        c45_dir=tmp_path,
        c45_summary=c45_summary,
        c44_summary={"aggregate": {"call_count": 2, "cost_usd": 0.02}},
        embedding_summary={"aggregate": {"embedding_usage": {"call_count": 1, "total_tokens": 10}}},
    )

    aggregate = result["aggregate"]
    assert aggregate["strict_lane_opportunity_count"] == 1
    assert aggregate["enhanced_opportunity_count"] == 1
    assert aggregate["safe_public_delta_count"] == 1
    assert aggregate["unsafe_public_delta_count"] == 1
    assert aggregate["strict_lane_safe_public_delta_count"] == 0
    assert aggregate["strict_lane_unsafe_public_delta_count"] == 1
    assert aggregate["enhanced_safe_public_delta_count"] == 1
    assert aggregate["enhanced_incremental_safe_public_delta_lower_bound"] == 1
