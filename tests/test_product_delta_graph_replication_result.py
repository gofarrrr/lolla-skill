from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from engine.system_b.product_delta_graph_replication import SAMPLE_ALIASES
from engine.system_b.product_delta_graph_replication_result import (
    BLIND_REVIEW_PACKET_RELPATH,
    COMPARISON_CASE_IDS,
    CONSOLIDATION_RELPATH,
    EXECUTION_SEALED_MANIFEST_RELPATH,
    POST_REVEAL_INTERPRETATION_RELPATHS,
    POST_REVEAL_PACKET_RELPATHS,
    REVIEW_FAILURE_RELPATHS,
    REVIEW_RELPATHS,
    SEALED_LINEAGE_MARKERS,
    ProductDeltaGraphReplicationResultError,
    _validate_review,
    build_blind_review_inputs,
    build_consolidation,
    build_post_reveal_packets,
    import_frozen_review,
    import_terminal_output,
    render_json,
    validate_checked_in_blind_review_inputs,
    validate_checked_in_complete_result,
    validate_checked_in_consolidation,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _build() -> tuple[dict[str, Any], dict[str, Any]]:
    return build_blind_review_inputs(repo_root=REPO_ROOT)


def test_all_eight_first_terminal_generations_are_admitted_once() -> None:
    blind, sealed = _build()

    receipts = sealed["generation_state_validation"]
    assert set(receipts) == set(SAMPLE_ALIASES)
    assert all(
        receipt["terminal_status"] == "complete"
        for receipt in receipts.values()
    )
    assert all(
        receipt["first_terminal_result_preserved"] is True
        for receipt in receipts.values()
    )
    assert all(
        receipt["all_active_candidates_accounted_for"] is True
        for receipt in receipts.values()
    )
    assert all(
        receipt["semantic_correctness_validated"] is False
        for receipt in receipts.values()
    )
    assert blind["boundary"]["repository_provider_api_calls"] == 0
    assert blind["boundary"]["repository_provider_api_cost_usd"] == 0.0


def test_blind_packet_has_eight_available_pairs_without_lineage() -> None:
    blind, sealed = _build()

    cases = blind["comparison_cases"]
    assert [case["case_id"] for case in cases] == list(COMPARISON_CASE_IDS)
    assert all(case["availability"] == "available" for case in cases)
    assert all(set(case["arms"]) == {"A", "B"} for case in cases)
    assert set(sealed["comparison_lineage"]) == set(COMPARISON_CASE_IDS)
    rendered = render_json(blind)
    for marker in SEALED_LINEAGE_MARKERS:
        assert marker not in rendered
    assert blind["visibility"]["condition_lineage_included"] is False
    assert blind["visibility"]["pair_roles_included"] is False
    availability = blind["pre_review_mechanical_availability"]
    assert availability["available_pair_count"] == 8
    assert availability["total_pair_count"] == 8
    assert availability["both_blind_reviews_complete"] is False


def test_checked_in_blind_inputs_are_exact_builder_products() -> None:
    blind, sealed = _build()

    assert (REPO_ROOT / BLIND_REVIEW_PACKET_RELPATH).read_text(
        encoding="utf-8"
    ) == render_json(blind)
    assert (REPO_ROOT / EXECUTION_SEALED_MANIFEST_RELPATH).read_text(
        encoding="utf-8"
    ) == render_json(sealed)
    assert validate_checked_in_blind_review_inputs(repo_root=REPO_ROOT) == []


def test_review_validator_records_unhashable_enum_shape_without_crashing() -> None:
    blind, _ = _build()
    review = json.loads(
        (REPO_ROOT / REVIEW_RELPATHS["primary"]).read_text(encoding="utf-8")
    )
    malformed = copy.deepcopy(review)
    malformed["duplicate_null_review"]["atomic_moves"][0][
        "cognitive_effect"
    ] = ["unsupported-list"]

    errors = _validate_review(
        malformed,
        expected_review_id=review["review_id"],
        blind=blind,
    )

    assert any("bad cognitive effect" in error for error in errors)


def test_primary_review_is_valid_and_skeptical_terminal_failure_is_exact() -> None:
    blind, _ = _build()
    primary = json.loads(
        (REPO_ROOT / REVIEW_RELPATHS["primary"]).read_text(encoding="utf-8")
    )
    assert _validate_review(
        primary,
        expected_review_id=primary["review_id"],
        blind=blind,
    ) == []

    raw_path = REPO_ROOT / REVIEW_RELPATHS["skeptical"]
    raw = raw_path.read_bytes()
    failure = json.loads(
        (REPO_ROOT / REVIEW_FAILURE_RELPATHS["skeptical"]).read_text(
            encoding="utf-8"
        )
    )
    assert failure["terminal_state"] == "failed"
    assert failure["failure_class"] == "review_shape_validation_failed"
    assert failure["validation_error_count"] == 29
    assert (
        failure["raw_first_terminal_payload"]["sha256"]
        == hashlib.sha256(raw).hexdigest()
    )
    assert failure[
        "retry_fallback_healing_replacement_or_imputation"
    ] is False
    assert not (REPO_ROOT / REVIEW_FAILURE_RELPATHS["primary"]).exists()


def test_review_failure_closes_gate_without_post_reveal_contexts() -> None:
    with pytest.raises(
        ProductDeltaGraphReplicationResultError,
        match="required blind review",
    ):
        build_post_reveal_packets(repo_root=REPO_ROOT)

    for relpath in (
        *POST_REVEAL_PACKET_RELPATHS.values(),
        *POST_REVEAL_INTERPRETATION_RELPATHS.values(),
    ):
        assert not (REPO_ROOT / relpath).exists()


def test_consolidation_preserves_honest_not_evaluable_closeout() -> None:
    result, errors = build_consolidation(repo_root=REPO_ROOT)

    assert errors == []
    assert result["status"] == (
        "valid_frozen_agent_replication_not_evaluable_"
        "required_blind_review_failure"
    )
    assert result["replication_interpretation"]["state"] == "not_evaluable"
    isolation = result["isolation_receipt"]
    assert isolation["generation_first_terminal_outputs_complete"] == 8
    assert isolation["generation_first_terminal_failures"] == 0
    assert isolation["blind_review_valid_terminal_results"] == 1
    assert isolation["blind_review_terminal_failures"] == 1
    assert isolation["post_reveal_contexts_started"] == 0
    assert isolation["lineage_reveal_performed"] is False
    assert result["boundary"]["winner_selected"] is False
    assert result["boundary"]["permission_to_expand_graph_created"] is False
    assert [review["lane"] for review in result["valid_blind_reviews"]] == [
        "primary"
    ]


def test_checked_in_consolidation_and_complete_result_are_current() -> None:
    result, errors = build_consolidation(repo_root=REPO_ROOT)

    assert errors == []
    assert (REPO_ROOT / CONSOLIDATION_RELPATH).read_text(
        encoding="utf-8"
    ) == render_json(result)
    assert validate_checked_in_consolidation(repo_root=REPO_ROOT) == []
    assert validate_checked_in_complete_result(repo_root=REPO_ROOT) == []


def test_imports_refuse_to_overwrite_frozen_terminal_states() -> None:
    with pytest.raises(
        ProductDeltaGraphReplicationResultError,
        match="already frozen",
    ):
        import_terminal_output(
            repo_root=REPO_ROOT,
            sample_alias="sample-amber",
            source_path=(
                REPO_ROOT
                / "research/agent-only-graph-replication-2026-07-23/"
                "terminal-output-sample-amber.json"
            ),
        )
    for lane in ("primary", "skeptical"):
        with pytest.raises(
            ProductDeltaGraphReplicationResultError,
            match="already frozen",
        ):
            import_frozen_review(
                repo_root=REPO_ROOT,
                lane=lane,
                source_path=REPO_ROOT / REVIEW_RELPATHS[lane],
            )


def test_cli_validates_complete_result() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_product_delta_graph_replication_result.py",
            "--validate-complete",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "complete result are current" in result.stdout
