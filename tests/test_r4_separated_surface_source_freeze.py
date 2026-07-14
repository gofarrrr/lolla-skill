from __future__ import annotations

from pathlib import Path

import json


ROOT = Path(__file__).resolve().parents[1]
HUMAN_CUSTODY = (
    ROOT
    / "research/lolla-r4-separated-surface-experiment-v1-source-freeze-2026-07-14"
    / "human-leakage-review-custody.json"
)


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


def test_source_freeze_manifest_reproduces_after_human_review_completion() -> None:
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
    assert "Status: human semantic-leakage review passed" in packet
    assert "Human finding: `passed`" in packet
    assert "Human finding: `pending`" not in packet
    for row in manifest["cases"]:
        assert row["source"]["path"] in packet
        assert row["source"]["sha256"] in packet
        assert row["prior"]["path"] in packet
        assert row["prior"]["sha256"] in packet


def test_post_review_boundary_contains_no_provider_package() -> None:
    from scripts.evals import build_r4_separated_surface_source_freeze as builder

    builder.validate_forbidden_artifact_absence()

    assert not (ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-contract.json").exists()
    assert not (ROOT / "scripts/evals/run_r4_separated_surface_experiment.py").exists()


def test_human_declaration_is_hash_bound_and_complete_before_target() -> None:
    from scripts.evals import build_r4_separated_surface_source_freeze as builder

    manifest = builder.build_manifest()
    custody = json.loads(HUMAN_CUSTODY.read_text(encoding="utf-8"))

    assert custody["declaration"] == (
        "human leakage review passes for R4 separated-surface source freeze v1"
    )
    assert custody["freeze_manifest_sha256"] == (
        "ee39536238421efb7d8c6b28a0c6acfcbf10d6f4cfc8064f8f6ad5bbd3919921"
    )
    assert custody["human_semantic_leakage_review"] == "passed"
    assert custody["target_authorship_allowed"] is True
    assert len(custody["cases"]) == 4

    by_id = {row["case_id"]: row for row in manifest["cases"]}
    for row in custody["cases"]:
        frozen = by_id[row["case_id"]]
        assert row["source_sha256"] == frozen["source"]["sha256"]
        assert row["prior_sha256"] == frozen["prior"]["sha256"]
        assert row["human_semantic_leakage_review"] == "passed"
        assert row["final_four_sufficient_for_both_surfaces"] is False
        assert row["final_four_sufficiency"] == {
            "residual_decision_gap": False,
            "residual_reconsideration_dependency": False,
        }
        assert set(row["question_findings"]) == {
            f"q{index:02d}" for index in range(1, 11)
        }
        assert all(
            finding["result"] == "passed"
            for finding in row["question_findings"].values()
        )
