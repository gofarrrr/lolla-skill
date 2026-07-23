from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_graph_variance_calibration_result import (
    BLIND_REVIEW_PACKET_RELPATH,
    COMPARISON_CASE_IDS,
    EXECUTION_SEALED_MANIFEST_RELPATH,
    FAILURE_RELPATHS,
    ProductDeltaGraphVarianceResultError,
    _resolve_repo_path,
    _validate_generation_states,
    build_blind_review_inputs,
    build_review_consolidation,
    import_frozen_review,
    render_json,
    validate_checked_in_blind_review_inputs,
    validate_checked_in_review_consolidation,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _build() -> tuple[dict[str, Any], dict[str, Any]]:
    return build_blind_review_inputs(repo_root=REPO_ROOT)


def test_generation_states_preserve_three_outputs_and_one_failure() -> None:
    blind, sealed = _build()

    receipts = sealed["generation_state_validation"]
    assert sorted(item["terminal_status"] for item in receipts.values()) == [
        "complete",
        "complete",
        "complete",
        "failed",
    ]
    failure = receipts["sample-moss"]
    assert failure["retry_fallback_healing_replacement_or_imputation"] is False
    assert not (
        REPO_ROOT
        / "research/agent-only-graph-variance-calibration-2026-07-23/"
        "terminal-output-sample-moss.json"
    ).exists()
    assert (REPO_ROOT / FAILURE_RELPATHS["sample-moss"]).exists()
    assert blind["boundary"]["repository_provider_api_calls"] == 0
    assert blind["boundary"]["repository_provider_api_cost_usd"] == 0.0


def test_five_predeclared_comparisons_survive_with_two_not_evaluable() -> None:
    blind, sealed = _build()

    cases = blind["comparison_cases"]
    assert [item["case_id"] for item in cases] == list(COMPARISON_CASE_IDS)
    assert [item["availability"] for item in cases] == [
        "not_evaluable",
        "available",
        "available",
        "available",
        "not_evaluable",
    ]
    assert all(item["arms"] == {} for item in (cases[0], cases[4]))
    assert all(set(item["arms"]) == {"A", "B"} for item in cases[1:4])
    assert set(sealed["comparison_lineage"]) == set(COMPARISON_CASE_IDS)
    assert sealed["handling"][
        "failed_sample_retried_healed_replaced_or_imputed"
    ] is False


def test_public_blind_packet_hides_lineage_and_candidate_ledgers() -> None:
    blind, _ = _build()
    rendered = render_json(blind)

    for marker in (
        "sample-cinder",
        "sample-linen",
        "sample-moss",
        "sample-slate",
        "within-direct-fresh",
        "within-graph-fresh",
        "cross-historical",
        "cross-fresh-1",
        "cross-fresh-2",
        "rehearsal_direct_plus_current_one_hop",
    ):
        assert marker not in rendered
    assert '"candidate_dispositions":' not in rendered
    assert blind["visibility"]["condition_lineage_included"] is False
    assert blind["visibility"]["pair_roles_included"] is False


def test_available_outputs_compile_against_their_frozen_portfolios() -> None:
    _, sealed = _build()

    receipts = sealed["generation_state_validation"]
    for alias in ("sample-cinder", "sample-linen", "sample-slate"):
        assert receipts[alias]["terminal_status"] == "complete"
        assert receipts[alias]["first_terminal_result_preserved"] is True
        assert receipts[alias]["all_active_candidates_accounted_for"] is True
        assert (
            receipts[alias]["invented_high_stakes_fact_or_causation_detected"]
            is False
        )


def test_checked_in_blind_inputs_are_exact_builder_products() -> None:
    blind, sealed = _build()

    assert (REPO_ROOT / BLIND_REVIEW_PACKET_RELPATH).read_text(
        encoding="utf-8"
    ) == render_json(blind)
    assert (REPO_ROOT / EXECUTION_SEALED_MANIFEST_RELPATH).read_text(
        encoding="utf-8"
    ) == render_json(sealed)
    assert validate_checked_in_blind_review_inputs(repo_root=REPO_ROOT) == []


def test_builder_fails_closed_if_failure_is_replaced_by_output(
    tmp_path: Path,
) -> None:
    for relpath in (
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "terminal-output-sample-cinder.json",
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "terminal-output-sample-linen.json",
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "terminal-output-sample-slate.json",
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "terminal-failure-sample-moss.json",
    ):
        source = REPO_ROOT / relpath
        target = tmp_path / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    replacement = (
        tmp_path
        / "research/agent-only-graph-variance-calibration-2026-07-23/"
        "terminal-output-sample-moss.json"
    )
    replacement.write_text(
        json.dumps(
            json.loads(
                (
                    REPO_ROOT
                    / "research/agent-only-graph-variance-calibration-2026-07-23/"
                    "terminal-output-sample-cinder.json"
                ).read_text(encoding="utf-8")
            )
        ),
        encoding="utf-8",
    )
    generation = json.loads(
        (
            REPO_ROOT
            / "research/agent-only-graph-variance-calibration-2026-07-23/"
            "generation-packets.json"
        ).read_text(encoding="utf-8")
    )
    sealed = json.loads(
        (
            REPO_ROOT
            / "research/agent-only-graph-variance-calibration-2026-07-23/"
            "sealed-manifest.json"
        ).read_text(encoding="utf-8")
    )
    bundle = json.loads(
        (
            REPO_ROOT
            / "research/consumer-context-role-attribution-case-candidate-2026-07-23/"
            "portfolio-bundle.json"
        ).read_text(encoding="utf-8")
    )
    try:
        _validate_generation_states(
            root=tmp_path,
            generation=generation,
            preoutput_sealed=sealed,
            bundle=bundle,
        )
    except ProductDeltaGraphVarianceResultError as exc:
        assert "both terminal output and terminal failure" in str(exc)
    else:
        raise AssertionError("a failed draw must not be replaced")


def test_path_resolution_rejects_escape() -> None:
    try:
        _resolve_repo_path(REPO_ROOT, "../outside.json")
    except ProductDeltaGraphVarianceResultError as exc:
        assert "escapes repository root" in str(exc)
    else:
        raise AssertionError("path escape must fail")


def test_cli_validates_checked_in_blind_inputs() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_product_delta_graph_variance_calibration_result.py",
            "--validate-only",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "blind review inputs are current" in result.stdout


def test_generated_artifacts_change_when_a_terminal_output_changes() -> None:
    blind, _ = _build()
    modified = copy.deepcopy(blind)
    modified["comparison_cases"][1]["arms"]["A"]["content"] += " changed"

    assert render_json(modified) != render_json(blind)


def test_consolidation_preserves_not_evaluable_result_and_pair_reads() -> None:
    result, errors = build_review_consolidation(repo_root=REPO_ROOT)

    assert errors == []
    assert result["status"] == (
        "valid_frozen_agent_diagnostic_not_evaluable_terminal_failure"
    )
    interpretation = result["calibration_interpretation"]
    assert interpretation["state"] == "not_evaluable"
    assert interpretation["available_comparison_case_ids"] == [
        "calibration-pair-02",
        "calibration-pair-03",
        "calibration-pair-04",
    ]
    assert interpretation["unavailable_comparison_case_ids"] == [
        "calibration-pair-01",
        "calibration-pair-05",
    ]
    comparisons = {
        item["case_id"]: item for item in result["comparison_reviews"]
    }
    assert [
        read["material_decision_difference"]
        for read in comparisons["calibration-pair-02"]["reviewer_reads"]
    ] == ["present", "present"]
    assert [
        read["material_decision_difference"]
        for read in comparisons["calibration-pair-03"]["reviewer_reads"]
    ] == ["present", "uncertain"]
    assert [
        read["material_decision_difference"]
        for read in comparisons["calibration-pair-04"]["reviewer_reads"]
    ] == ["present", "present"]


def test_controls_and_isolation_survive_consolidation() -> None:
    result, errors = build_review_consolidation(repo_root=REPO_ROOT)

    assert errors == []
    assert [
        read["material_decision_difference"]
        for read in result["duplicate_null_review"]["reviewer_reads"]
    ] == ["absent", "absent"]
    assert [
        read["standdown_support"]
        for read in result["standdown_reviews"][0]["reviewer_reads"]
    ] == ["supported", "supported"]
    isolation = result["isolation_receipt"]
    assert isolation["generation_first_terminal_outputs_complete"] == 3
    assert isolation["generation_first_terminal_failures"] == 1
    assert (
        isolation[
            "generation_retries_fallbacks_healing_replacements_or_imputations"
        ]
        == 0
    )
    assert isolation["reviewers_saw_lineage_before_freeze"] is False
    assert isolation["reviewers_saw_each_other_before_freeze"] is False
    assert result["boundary"]["scalar_summary_created"] is False
    assert result["boundary"]["winner_selected"] is False


def test_checked_in_consolidation_is_exact_builder_product() -> None:
    assert validate_checked_in_review_consolidation(repo_root=REPO_ROOT) == []


def test_import_refuses_to_overwrite_a_frozen_review() -> None:
    source = (
        REPO_ROOT
        / "reviews/codex-assisted/agent-only-graph-variance-calibration-v1/"
        "pair-review-primary.json"
    )
    try:
        import_frozen_review(
            repo_root=REPO_ROOT,
            lane="primary",
            source_path=source,
        )
    except ProductDeltaGraphVarianceResultError as exc:
        assert "overwrite forbidden" in str(exc)
    else:
        raise AssertionError("a frozen first-terminal review must not change")


def test_cli_validates_complete_result() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_product_delta_graph_variance_calibration_result.py",
            "--validate-complete",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "calibration result is current" in result.stdout
