from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from engine.system_b.product_delta_graph_increment_rehearsal import (
    REHEARSAL_DIRECT,
    REHEARSAL_DIRECT_PLUS_ONE_HOP,
)
from engine.system_b.product_delta_graph_replication import (
    DEFAULT_GENERATION_PACKETS_RELPATH,
    DEFAULT_SEALED_MANIFEST_RELPATH,
    DRAW_NUMBERS,
    GENERATION_PACKETS_SCHEMA_VERSION,
    SAMPLE_ALIASES,
    SEALED_MANIFEST_SCHEMA_VERSION,
    ProductDeltaGraphReplicationError,
    _resolve_repo_path,
    build_graph_replication,
    evaluate_mechanical_availability,
    render_json,
    validate_checked_in_replication,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _build() -> tuple[dict[str, Any], dict[str, Any]]:
    return build_graph_replication(repo_root=REPO_ROOT)


def _read_json(relpath: str) -> dict[str, Any]:
    payload = json.loads((REPO_ROOT / relpath).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_eight_neutral_samples_are_balanced_and_use_draws_three_to_six() -> None:
    generation, sealed = _build()

    assert generation["schema_version"] == GENERATION_PACKETS_SCHEMA_VERSION
    assert generation["sample_count"] == 8
    assert generation["sample_aliases"] == list(SAMPLE_ALIASES)
    assert generation["execution_order"] == list(SAMPLE_ALIASES)
    assert sealed["schema_version"] == SEALED_MANIFEST_SCHEMA_VERSION

    counts = {REHEARSAL_DIRECT: 0, REHEARSAL_DIRECT_PLUS_ONE_HOP: 0}
    draws = {REHEARSAL_DIRECT: set(), REHEARSAL_DIRECT_PLUS_ONE_HOP: set()}
    for item in sealed["sample_map"].values():
        counts[item["condition"]] += 1
        draws[item["condition"]].add(item["draw_number"])
    assert counts == {
        REHEARSAL_DIRECT: 4,
        REHEARSAL_DIRECT_PLUS_ONE_HOP: 4,
    }
    assert draws == {
        REHEARSAL_DIRECT: set(DRAW_NUMBERS),
        REHEARSAL_DIRECT_PLUS_ONE_HOP: set(DRAW_NUMBERS),
    }


def test_each_sample_inherits_one_completed_variance_packet_exactly() -> None:
    generation, sealed = _build()
    predecessor_generation = _read_json(
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "generation-packets.json"
    )
    predecessor_sealed = _read_json(
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "sealed-manifest.json"
    )
    predecessor_by_condition: dict[str, dict[str, Any]] = {}
    packet_by_alias = {
        item["sample_alias"]: item
        for item in predecessor_generation["packets"]
    }
    for alias, lineage in predecessor_sealed["sample_map"].items():
        predecessor_by_condition.setdefault(
            lineage["condition"], packet_by_alias[alias]
        )

    for sample in generation["packets"]:
        lineage = sealed["sample_map"][sample["sample_alias"]]
        predecessor = predecessor_by_condition[lineage["condition"]]
        assert (
            sample["request_body_projection"]
            == predecessor["request_body_projection"]
        )
        assert sample["codex_task_wrapper"] == predecessor["codex_task_wrapper"]
        assert sample["execution"]["performed"] is False
        assert sample["execution"]["retry_or_fallback_authorized"] is False
        assert sample["restart_safe_terminal_capture"] == {
            "required": True,
            "method": (
                "codex_exec_output_last_message_direct_to_"
                "predeclared_external_path"
            ),
            "first_terminal_payload_only": True,
            "event_log_or_session_reconstruction_forbidden": True,
            "retry_healing_fallback_or_replacement_forbidden": True,
        }


def test_public_packet_metadata_does_not_reveal_condition_or_draw_lineage() -> None:
    generation, _ = _build()
    metadata_only = copy.deepcopy(generation)
    for packet in metadata_only["packets"]:
        packet["request_body_projection"] = "[exact semantic packet omitted]"
        packet["codex_task_wrapper"] = "[exact wrapper omitted]"
    rendered = render_json(metadata_only)

    assert "rehearsal_direct_plus_current_one_hop" not in rendered
    assert 'rehearsal_direct"' not in rendered
    assert "draw_number" not in rendered
    assert "source_variance_sample_alias" not in rendered


def test_comparison_plan_is_disjoint_within_role_and_aligned_cross_role() -> None:
    _, sealed = _build()
    plan = sealed["comparison_plan"]

    assert len(plan) == 8
    assert [item["sealed_pair_role"] for item in plan].count(
        "within_condition"
    ) == 4
    assert [item["sealed_pair_role"] for item in plan].count(
        "cross_condition"
    ) == 4
    usage = {
        alias: {"within": 0, "cross": 0} for alias in SAMPLE_ALIASES
    }
    for item in plan:
        role = (
            "within"
            if item["sealed_pair_role"] == "within_condition"
            else "cross"
        )
        for side in ("left", "right"):
            usage[item[side]["sample_alias"]][role] += 1
    assert all(
        item == {"within": 1, "cross": 1} for item in usage.values()
    )


def test_availability_gate_survives_any_one_generation_failure() -> None:
    _, sealed = _build()

    for failed_alias in SAMPLE_ALIASES:
        states = {alias: "complete" for alias in SAMPLE_ALIASES}
        states[failed_alias] = "failed"
        receipt = evaluate_mechanical_availability(
            sealed_manifest=sealed,
            sample_terminal_states=states,
            both_blind_reviews_complete=True,
        )
        assert receipt["gate_passes"] is True
        assert receipt["result_if_closed_now"] == (
            "eligible_for_post_reveal_interpretation"
        )
        assert receipt["available_counts"]["cross_condition"] == 3


def test_availability_gate_fails_without_one_within_baseline_or_reviews() -> None:
    _, sealed = _build()
    direct_aliases_by_draw = {
        lineage["draw_number"]: alias
        for alias, lineage in sealed["sample_map"].items()
        if lineage["condition"] == REHEARSAL_DIRECT
    }
    states = {alias: "complete" for alias in SAMPLE_ALIASES}
    states[direct_aliases_by_draw[3]] = "failed"
    states[direct_aliases_by_draw[5]] = "failed"

    receipt = evaluate_mechanical_availability(
        sealed_manifest=sealed,
        sample_terminal_states=states,
        both_blind_reviews_complete=True,
    )
    assert receipt["available_counts"]["within_direct"] == 0
    assert receipt["gate_passes"] is False
    assert receipt["result_if_closed_now"] == "not_evaluable"

    complete_states = {alias: "complete" for alias in SAMPLE_ALIASES}
    missing_reviews = evaluate_mechanical_availability(
        sealed_manifest=sealed,
        sample_terminal_states=complete_states,
        both_blind_reviews_complete=False,
    )
    assert missing_reviews["gate_passes"] is False
    assert missing_reviews["result_if_closed_now"] == "not_evaluable"


def test_availability_gate_rejects_alias_or_state_drift() -> None:
    _, sealed = _build()
    missing_alias = {
        alias: "complete" for alias in SAMPLE_ALIASES if alias != "sample-amber"
    }
    with pytest.raises(
        ProductDeltaGraphReplicationError,
        match="aliases do not match",
    ):
        evaluate_mechanical_availability(
            sealed_manifest=sealed,
            sample_terminal_states=missing_alias,
            both_blind_reviews_complete=True,
        )

    invalid_state = {alias: "complete" for alias in SAMPLE_ALIASES}
    invalid_state["sample-amber"] = "completed_zero"
    with pytest.raises(
        ProductDeltaGraphReplicationError,
        match="state vocabulary",
    ):
        evaluate_mechanical_availability(
            sealed_manifest=sealed,
            sample_terminal_states=invalid_state,
            both_blind_reviews_complete=True,
        )


def test_boundary_preserves_zero_provider_and_no_product_change() -> None:
    generation, sealed = _build()

    for payload in (generation, sealed):
        boundary = payload["boundary"]
        assert boundary["repository_provider_api_calls"] == 0
        assert boundary["repository_provider_api_cost_usd"] == 0.0
        assert boundary["graph_traversal_invoked"] is False
        assert boundary["graph_source_or_relation_changed"] is False
        assert boundary["graph_policy_changed"] is False
        assert boundary["planner_changed"] is False
        assert boundary["compiler_changed"] is False
        assert boundary["runtime_invoked"] is False
        assert boundary["live_skill_invoked"] is False
        assert boundary["graph_causation_established"] is False
        assert boundary["human_usefulness_established"] is False


def test_checked_in_outputs_are_exact_builder_products() -> None:
    generation, sealed = _build()
    for relpath, payload in (
        (DEFAULT_GENERATION_PACKETS_RELPATH, generation),
        (DEFAULT_SEALED_MANIFEST_RELPATH, sealed),
    ):
        assert (REPO_ROOT / relpath).read_text(
            encoding="utf-8"
        ) == render_json(payload)
    assert validate_checked_in_replication(repo_root=REPO_ROOT) == []


def test_builder_fails_closed_on_locked_input_drift(tmp_path: Path) -> None:
    relpaths = [
        "docs/evals/lolla-agent-only-graph-replication-contract-v1.json",
        "docs/evals/lolla-agent-only-graph-variance-calibration-contract-v1.json",
        "docs/evals/lolla-agent-only-graph-increment-rehearsal-contract-v1.json",
        "docs/evals/lolla-agent-only-paired-delta-screen-contract-v1.json",
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "generation-packets.json",
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "sealed-manifest.json",
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "consolidated-diagnostic.json",
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "blind-review-packet.json",
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "execution-sealed-manifest.json",
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "terminal-output-sample-cinder.json",
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "terminal-failure-sample-moss.json",
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "terminal-output-sample-slate.json",
        "research/agent-only-graph-variance-calibration-2026-07-23/"
        "terminal-output-sample-linen.json",
        "reviews/codex-assisted/agent-only-graph-variance-calibration-v1/"
        "pair-review-primary.json",
        "reviews/codex-assisted/agent-only-graph-variance-calibration-v1/"
        "pair-review-skeptical.json",
        "research/agent-only-graph-increment-rehearsal-2026-07-23/"
        "generation-packets.json",
        "research/agent-only-graph-increment-rehearsal-2026-07-23/"
        "sealed-manifest.json",
        "research/agent-only-graph-increment-rehearsal-2026-07-23/"
        "consolidated-diagnostic.json",
        "research/agent-only-graph-increment-rehearsal-2026-07-23/"
        "terminal-output-condition-A.json",
        "research/agent-only-graph-increment-rehearsal-2026-07-23/"
        "terminal-output-condition-B.json",
        "research/independent-phase5-cases-2026-07-12/"
        "useful-pressure-case.txt",
    ]
    for relpath in relpaths:
        source = REPO_ROOT / relpath
        target = tmp_path / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    drifted = (
        tmp_path
        / "research/agent-only-graph-variance-calibration-2026-07-23/"
        "generation-packets.json"
    )
    drifted.write_text("{}\n", encoding="utf-8")

    with pytest.raises(
        ProductDeltaGraphReplicationError,
        match="predecessor",
    ):
        build_graph_replication(repo_root=tmp_path)


def test_path_resolution_rejects_escape() -> None:
    with pytest.raises(
        ProductDeltaGraphReplicationError,
        match="escapes repository root",
    ):
        _resolve_repo_path(REPO_ROOT, "../outside.json")


def test_cli_validates_checked_in_replication() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_product_delta_graph_replication.py",
            "--validate-only",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "artifacts are current" in result.stdout
