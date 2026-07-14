from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_source_prior_portfolio_has_exact_structure_and_zero_lint_matches() -> None:
    from scripts.evals import build_r4_separated_surface_source_freeze as builder

    cases = builder.load_and_validate_cases()

    assert list(cases) == list(builder.CASE_SPECS)
    assert len(cases) == 4
    assert len({case["source"]["domain"] for case in cases.values()}) == 4
    assert builder.lint_cases(cases) == []

    for case_id, case in cases.items():
        source = case["source"]
        prior = case["prior"]
        assert source["case_id"] == case_id
        assert source["message_count"] == 28
        assert len(source["messages"]) == 28
        assert [row["alias"] for row in source["messages"]] == [
            f"e{index:03d}" for index in range(1, 29)
        ]
        assert [row["speaker"] for row in source["messages"]] == [
            "user" if index % 2 else "assistant" for index in range(1, 29)
        ]
        assert prior["case_id"] == case_id
        assert prior["artifact_kind"] == "fallible_prior_interpretation"
        assert prior["authority"] == "fallible_prior_interpretation_not_source_truth"
        assert [row["surface"] for row in prior["records"]] == [
            "starting_position",
            "current_position",
            "qualification",
        ]


def test_freeze_manifest_reproduces_and_human_gate_remains_pending() -> None:
    from scripts.evals import build_r4_separated_surface_source_freeze as builder

    manifest = builder.validate()

    assert manifest["status"] == "source_prior_frozen_human_review_pending_before_target"
    assert manifest["provider_calls"] == 0
    assert manifest["provider_cost_usd"] == 0.0
    assert manifest["target_existed_when_frozen"] is False
    assert manifest["request_preview_existed_when_frozen"] is False
    assert manifest["provider_output_existed_when_frozen"] is False
    assert manifest["human_semantic_leakage_review"] == "pending"
    assert manifest["target_authorship_allowed"] is False
    assert len(manifest["cases"]) == 4
    assert all(row["source"]["message_count"] == 28 for row in manifest["cases"])
    assert all(row["source"]["alias_count"] == 28 for row in manifest["cases"])
    assert all(row["prior"]["record_count"] == 3 for row in manifest["cases"])
    assert all(row["deterministic_prohibited_language_matches"] == 0 for row in manifest["cases"])

    packet = builder.HUMAN_REVIEW_PACKET.read_text(encoding="utf-8")
    assert "Status: pending human semantic-leakage review" in packet
    assert "Human finding: `pending`" in packet
    assert "Human finding: `passed`" not in packet
    for row in manifest["cases"]:
        assert row["source"]["path"] in packet
        assert row["source"]["sha256"] in packet
        assert row["prior"]["path"] in packet
        assert row["prior"]["sha256"] in packet


def test_pre_target_boundary_contains_no_forbidden_artifacts() -> None:
    from scripts.evals import build_r4_separated_surface_source_freeze as builder

    builder.validate_forbidden_artifact_absence()

    assert not (ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-target.json").exists()
    assert not (ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-target-review.json").exists()
    assert not (ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-contract.json").exists()
    assert not (ROOT / "scripts/evals/run_r4_separated_surface_experiment.py").exists()
