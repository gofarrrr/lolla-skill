from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_paired_screen import (
    CONTRACT_SCHEMA_VERSION,
    DEFAULT_BLIND_PACKETS_RELPATH,
    DEFAULT_CONTRACT_RELPATH,
    DEFAULT_SEALED_MANIFEST_RELPATH,
    PAIRED_SCREEN_SCHEMA_VERSION,
    SEALED_MANIFEST_SCHEMA_VERSION,
    build_product_delta_paired_screen,
    render_json,
)
from engine.system_b.product_delta_paired_screen_review import (
    CONSOLIDATION_SCHEMA_VERSION,
    DEFAULT_CONSOLIDATION_RELPATH,
    build_review_consolidation,
    render_json as render_review_json,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _build() -> tuple[dict[str, Any], dict[str, Any]]:
    return build_product_delta_paired_screen(repo_root=REPO_ROOT)


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_walk_keys(child))
    return keys


def test_screen_has_mixed_corpus_without_flattening_evidence_classes() -> None:
    blind, sealed = _build()

    assert blind["schema_version"] == PAIRED_SCREEN_SCHEMA_VERSION
    assert sealed["schema_version"] == SEALED_MANIFEST_SCHEMA_VERSION
    assert blind["qualification_case_count"] == 10
    assert blind["paired_case_count"] == 7
    assert blind["standdown_case_count"] == 1
    counts: dict[str, int] = {}
    for case in blind["paired_cases"]:
        evidence_class = case["evidence_class"]
        counts[evidence_class] = counts.get(evidence_class, 0) + 1
    assert counts == {
        "complete_exact_pair": 3,
        "partial_source_view_research_calibration": 3,
        "exact_duplicate_null": 1,
    }


def test_boundary_is_provider_free_and_non_authoritative() -> None:
    blind, sealed = _build()

    for boundary in (blind["boundary"], sealed["boundary"]):
        assert boundary["provider_calls"] == 0
        assert boundary["provider_cost_usd"] == 0
        assert boundary["private_archives_read"] is False
        assert boundary["runtime_invoked"] is False
        assert boundary["graph_traversal_invoked"] is False
        assert boundary["graph_or_runtime_changed"] is False
        assert boundary["human_validated"] is False
        assert boundary["ground_truth"] is False
        assert boundary["product_proof"] is False
        assert boundary["answer_quality_scored"] is False
        assert boundary["scalar_judgment_created"] is False


def test_blind_packets_exclude_lineage_and_prior_judgments() -> None:
    blind, _ = _build()
    rendered = render_json(blind)
    keys = _walk_keys(blind)

    assert "arm_map" not in keys
    assert "historical_refs" not in keys
    assert "baseline_locator" not in keys
    assert "added_context_locator" not in keys
    assert "aggregate_decision" not in keys
    assert "strong_reconsideration_control" not in rendered
    assert "lolla_pressure_treatment" not in rendered
    assert "pressure_wins" not in rendered
    assert "raw_wins" not in rendered
    assert "tie_stop" not in rendered
    assert "requested_model" not in rendered
    assert "served_model" not in rendered


def test_qualification_packets_hide_expectations_and_forbidden_answers() -> None:
    blind, _ = _build()
    rendered = json.dumps(blind["qualification_cases"], sort_keys=True)
    keys = _walk_keys(blind["qualification_cases"])

    assert len(blind["qualification_cases"]) == 10
    assert "expected_provisional_behavior" not in keys
    assert "forbidden_behavior" not in keys
    assert "human_review_note" not in keys
    assert "why_this_matters" not in keys
    assert "material_improvement_candidate" not in rendered


def test_null_pair_is_byte_equivalent_after_normalization() -> None:
    blind, sealed = _build()
    null_case = next(
        case
        for case in blind["paired_cases"]
        if case["evidence_class"] == "exact_duplicate_null"
    )
    null_manifest = next(
        case
        for case in sealed["paired_cases"]
        if case["evidence_class"] == "exact_duplicate_null"
    )

    assert null_case["arms"]["A"] == null_case["arms"]["B"]
    assert (
        null_manifest["arm_map"]["A"]["content_sha256"]
        == null_manifest["arm_map"]["B"]["content_sha256"]
    )


def test_blinding_is_stable_and_uses_both_orientations() -> None:
    _, first_sealed = _build()
    _, second_sealed = _build()

    assert first_sealed == second_sealed
    added_labels = {
        label
        for case in first_sealed["paired_cases"]
        for label, arm in case["arm_map"].items()
        if arm["origin"] == "reconsideration_with_added_external_context"
    }
    assert added_labels == {"A", "B"}


def test_complete_and_partial_source_custody_remain_distinct() -> None:
    blind, _ = _build()
    exact_cases = [
        case
        for case in blind["paired_cases"]
        if case["evidence_class"] == "complete_exact_pair"
    ]
    partial_cases = [
        case
        for case in blind["paired_cases"]
        if case["evidence_class"]
        == "partial_source_view_research_calibration"
    ]

    assert all(
        case["source"]["coverage"] == "complete_checked_in_conversation"
        for case in exact_cases
    )
    assert all(
        case["source"]["coverage"] == "partial_checked_in_source_excerpts"
        for case in partial_cases
    )
    assert all(
        "Partial source view only"
        in case["source"]["content"]["coverage_notice"]
        for case in partial_cases
    )


def test_review_contract_has_no_scalar_or_arm_selection_field() -> None:
    contract = json.loads(
        (REPO_ROOT / DEFAULT_CONTRACT_RELPATH).read_text(encoding="utf-8")
    )
    keys = _walk_keys(contract["blind_review_contract"])
    forbidden = {
        "winner",
        "score",
        "rating",
        "rank",
        "approved",
        "certified",
        "pass_fail",
        "better_arm",
    }

    assert contract["schema_version"] == CONTRACT_SCHEMA_VERSION
    assert not (keys & forbidden)
    assert "material_decision_difference" in keys
    assert "identity_guess_after_substantive_review" in keys
    assert "inspection_limits" in keys


def test_sealed_manifest_records_custody_without_semantic_answer_key() -> None:
    _, sealed = _build()
    rendered = render_json(sealed)

    assert sealed["handling"]["show_to_fresh_reviewers"] is False
    assert (
        sealed["handling"]["unblind_only_after_substantive_reviews_are_frozen"]
        is True
    )
    assert len(sealed["excluded_checked_in_product_delta_cases"]) == 14
    assert "aggregate_decision" not in rendered
    assert '"winner"' not in rendered
    assert '"score"' not in rendered
    assert "/Users/" not in rendered


def test_checked_in_artifacts_are_exact_builder_output() -> None:
    blind, sealed = _build()

    assert (REPO_ROOT / DEFAULT_BLIND_PACKETS_RELPATH).read_text(
        encoding="utf-8"
    ) == render_json(blind)
    assert (REPO_ROOT / DEFAULT_SEALED_MANIFEST_RELPATH).read_text(
        encoding="utf-8"
    ) == render_json(sealed)


def test_cli_validate_only() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_product_delta_paired_screen.py",
            "--validate-only",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "artifacts are current" in result.stdout


def test_outputs_have_no_local_paths_or_secret_markers() -> None:
    blind, sealed = _build()
    rendered = render_json(blind) + render_json(sealed)

    for marker in (
        "/Users/",
        "SECRET",
        "client_secret",
        "api_key",
        "password",
        "FULL ASSISTANT REASONING",
    ):
        assert marker not in rendered


def test_fresh_reviews_validate_and_preserve_disagreement() -> None:
    consolidation, errors = build_review_consolidation(repo_root=REPO_ROOT)

    assert errors == []
    assert consolidation["schema_version"] == CONSOLIDATION_SCHEMA_VERSION
    assert consolidation["status"] == "valid_frozen_agent_diagnostic"
    assert consolidation["validation"] == {
        "error_count": 0,
        "errors": [],
        "shape_and_custody_only": True,
        "semantic_correctness_validated": False,
    }
    assert consolidation["review_contexts"]["fresh_agent_context_count"] == 2
    assert consolidation["review_contexts"]["pair_reviewers_saw_each_other"] is False
    assert (
        consolidation["review_contexts"][
            "reviewers_saw_sealed_manifest_before_freeze"
        ]
        is False
    )
    assert set(
        consolidation["cross_case_observations"][
            "material_difference_disagreement_case_ids"
        ]
    ) == {"consulting-launch-exact", "phd-direction-partial"}


def test_consolidation_preserves_null_standdown_and_blinding_result() -> None:
    consolidation, _ = build_review_consolidation(repo_root=REPO_ROOT)
    observations = consolidation["cross_case_observations"]

    assert observations["duplicate_null_material_reads"] == ["absent", "absent"]
    assert observations["standdown_reads"] == [
        {"review_id": "fresh-pair-primary", "standdown_support": "supported"},
        {"review_id": "fresh-pair-skeptical", "standdown_support": "supported"},
    ]
    assert observations["identity_guess_relation_counts_excluding_null"] == {
        "matches_lineage": 6,
        "does_not_match_lineage": 5,
        "declared_indistinguishable": 1,
    }


def test_consolidation_does_not_vote_score_or_create_human_authority() -> None:
    consolidation, _ = build_review_consolidation(repo_root=REPO_ROOT)
    keys = _walk_keys(consolidation)
    forbidden = {
        "winner",
        "score",
        "rating",
        "rank",
        "approved",
        "certified",
        "pass_fail",
        "better_arm",
    }

    assert not (keys & forbidden)
    assert consolidation["boundary"]["new_provider_calls"] == 0
    assert consolidation["boundary"]["human_validated"] is False
    assert consolidation["boundary"]["ground_truth"] is False
    assert consolidation["boundary"]["product_proof"] is False
    assert consolidation["boundary"]["answer_quality_scored"] is False
    assert (
        consolidation["boundary"][
            "historical_provider_outputs_consumed_as_checked_in_inputs"
        ]
        is True
    )


def test_checked_in_consolidation_is_exact_builder_output() -> None:
    consolidation, errors = build_review_consolidation(repo_root=REPO_ROOT)

    assert errors == []
    assert (REPO_ROOT / DEFAULT_CONSOLIDATION_RELPATH).read_text(
        encoding="utf-8"
    ) == render_review_json(consolidation)


def test_review_validation_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/validate_product_delta_paired_screen_reviews.py",
            "--validate-only",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "reviews and consolidation are valid" in result.stdout
