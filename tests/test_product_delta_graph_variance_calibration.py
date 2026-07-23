from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_graph_increment_rehearsal import (
    REHEARSAL_DIRECT,
    REHEARSAL_DIRECT_PLUS_ONE_HOP,
)
from engine.system_b.product_delta_graph_variance_calibration import (
    DEFAULT_GENERATION_PACKETS_RELPATH,
    DEFAULT_SEALED_MANIFEST_RELPATH,
    GENERATION_PACKETS_SCHEMA_VERSION,
    SAMPLE_ALIASES,
    SEALED_MANIFEST_SCHEMA_VERSION,
    ProductDeltaGraphVarianceCalibrationError,
    _resolve_repo_path,
    build_graph_variance_calibration,
    render_json,
    validate_checked_in_calibration,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _build() -> tuple[dict[str, Any], dict[str, Any]]:
    return build_graph_variance_calibration(repo_root=REPO_ROOT)


def _read_json(relpath: str) -> dict[str, Any]:
    payload = json.loads((REPO_ROOT / relpath).read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_four_neutral_samples_are_exactly_balanced_between_conditions() -> None:
    generation, sealed = _build()

    assert generation["schema_version"] == GENERATION_PACKETS_SCHEMA_VERSION
    assert generation["sample_count"] == 4
    assert generation["sample_aliases"] == list(SAMPLE_ALIASES)
    assert [item["sample_alias"] for item in generation["packets"]] == list(
        SAMPLE_ALIASES
    )
    assert sealed["schema_version"] == SEALED_MANIFEST_SCHEMA_VERSION
    counts = {REHEARSAL_DIRECT: 0, REHEARSAL_DIRECT_PLUS_ONE_HOP: 0}
    draws = {REHEARSAL_DIRECT: set(), REHEARSAL_DIRECT_PLUS_ONE_HOP: set()}
    for item in sealed["sample_map"].values():
        counts[item["condition"]] += 1
        draws[item["condition"]].add(item["replicate_number"])
    assert counts == {
        REHEARSAL_DIRECT: 2,
        REHEARSAL_DIRECT_PLUS_ONE_HOP: 2,
    }
    assert draws == {
        REHEARSAL_DIRECT: {1, 2},
        REHEARSAL_DIRECT_PLUS_ONE_HOP: {1, 2},
    }


def test_each_sample_inherits_one_predecessor_request_and_wrapper_exactly() -> None:
    generation, sealed = _build()
    predecessor_generation = _read_json(
        "research/agent-only-graph-increment-rehearsal-2026-07-23/"
        "generation-packets.json"
    )
    predecessor_sealed = _read_json(
        "research/agent-only-graph-increment-rehearsal-2026-07-23/"
        "sealed-manifest.json"
    )
    predecessor_by_condition = {}
    packet_by_alias = {
        item["condition_alias"]: item
        for item in predecessor_generation["packets"]
    }
    for alias, lineage in predecessor_sealed["alias_map"].items():
        predecessor_by_condition[lineage["condition"]] = packet_by_alias[alias]

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


def test_public_generation_packet_metadata_does_not_reveal_sample_lineage() -> None:
    generation, _ = _build()
    metadata_only = copy.deepcopy(generation)
    for packet in metadata_only["packets"]:
        packet["request_body_projection"] = "[exact semantic packet omitted]"
    rendered = render_json(metadata_only)

    assert "rehearsal_direct_plus_current_one_hop" not in rendered
    assert "rehearsal_direct\"" not in rendered
    assert "condition-A" not in rendered
    assert "condition-B" not in rendered
    assert "replicate_number" not in rendered


def test_historical_draw_zero_and_five_pair_roles_are_predeclared() -> None:
    _, sealed = _build()

    assert set(sealed["historical_draw_zero"]) == {
        REHEARSAL_DIRECT,
        REHEARSAL_DIRECT_PLUS_ONE_HOP,
    }
    assert {
        item["draw_number"]
        for item in sealed["historical_draw_zero"].values()
    } == {0}
    plan = sealed["comparison_plan"]
    assert [item["pair_id"] for item in plan] == [
        "within-direct-fresh",
        "within-graph-fresh",
        "cross-historical",
        "cross-fresh-1",
        "cross-fresh-2",
    ]
    assert [
        item["sealed_pair_role"] for item in plan
    ].count("within_condition") == 2
    assert [
        item["sealed_pair_role"] for item in plan
    ].count("cross_condition") == 3


def test_boundary_preserves_zero_provider_and_no_product_change() -> None:
    generation, sealed = _build()

    for payload in (generation, sealed):
        boundary = payload["boundary"]
        assert boundary["repository_provider_api_calls"] == 0
        assert boundary["repository_provider_api_cost_usd"] == 0.0
        assert boundary["graph_traversal_invoked"] is False
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
    assert validate_checked_in_calibration(repo_root=REPO_ROOT) == []


def test_builder_fails_closed_on_locked_predecessor_drift(tmp_path: Path) -> None:
    for relpath in (
        "docs/evals/lolla-agent-only-graph-variance-calibration-contract-v1.json",
        "docs/evals/lolla-agent-only-graph-increment-rehearsal-contract-v1.json",
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
    ):
        source = REPO_ROOT / relpath
        target = tmp_path / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    drifted = (
        tmp_path
        / "research/agent-only-graph-increment-rehearsal-2026-07-23/"
        "terminal-output-condition-A.json"
    )
    drifted.write_text("{}\n", encoding="utf-8")

    try:
        build_graph_variance_calibration(repo_root=tmp_path)
    except ProductDeltaGraphVarianceCalibrationError as exc:
        assert "completed predecessor validation failed" in str(exc)
    else:
        raise AssertionError("predecessor drift must fail closed")


def test_path_resolution_rejects_escape() -> None:
    try:
        _resolve_repo_path(REPO_ROOT, "../outside.json")
    except ProductDeltaGraphVarianceCalibrationError as exc:
        assert "escapes repository root" in str(exc)
    else:
        raise AssertionError("path escape should fail")


def test_cli_validates_checked_in_calibration() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_product_delta_graph_variance_calibration.py",
            "--validate-only",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "artifacts are current" in result.stdout
