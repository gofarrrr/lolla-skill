from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from engine.system_b.product_delta_graph_increment_rehearsal import (
    CONDITION_ALIASES,
    DEFAULT_CONTRACT_RELPATH,
    DEFAULT_GENERATION_PACKETS_RELPATH,
    DEFAULT_POST_SEAL_PACKET_RELPATH,
    DEFAULT_SEALED_MANIFEST_RELPATH,
    DEFAULT_SOURCE_FIRST_PACKET_RELPATH,
    F2_CELL_ID,
    F2_PREVIEW_RELPATH,
    F3_CELL_ID,
    F3_PREVIEW_RELPATH,
    GENERATION_PACKETS_SCHEMA_VERSION,
    POST_SEAL_PACKET_SCHEMA_VERSION,
    ProductDeltaGraphIncrementRehearsalError,
    SEALED_MANIFEST_SCHEMA_VERSION,
    SOURCE_FIRST_PACKET_SCHEMA_VERSION,
    SOURCE_RELPATH,
    REHEARSAL_DIRECT,
    REHEARSAL_DIRECT_PLUS_ONE_HOP,
    _resolve_repo_path,
    build_graph_increment_rehearsal,
    render_json,
)
from engine.system_b.product_delta_paired_screen import (
    validate_checked_in_screen,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    return build_graph_increment_rehearsal(repo_root=REPO_ROOT)


def _read_json(relpath: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / relpath).read_text(encoding="utf-8"))


def test_source_first_packet_preserves_exact_source_custody() -> None:
    source_first, _, _, sealed = _build()
    source_bytes = (REPO_ROOT / SOURCE_RELPATH).read_bytes()

    assert source_first["schema_version"] == SOURCE_FIRST_PACKET_SCHEMA_VERSION
    assert (
        source_first["authoritative_source"]["content"].encode("utf-8")
        == source_bytes
    )
    assert (
        source_first["authoritative_source"]["sha256"]
        == sealed["input_refs"]["authoritative_source"]["sha256"]
    )
    assert source_first["authoritative_source"]["omissions"] == []
    assert (
        source_first["authoritative_source"]["utf8_bytes"]
        == len(source_bytes)
    )


def test_source_first_packet_has_no_candidate_or_lineage_artifacts() -> None:
    source_first, _, _, _ = _build()
    without_authoritative_words = copy.deepcopy(source_first)
    without_authoritative_words["authoritative_source"]["content"] = (
        "[authoritative source words intentionally removed for this assertion]"
    )
    rendered = render_json(without_authoritative_words)

    for forbidden in (
        "signaling",
        "social-proof",
        "confirmation-bias",
        "constitutional_graph_pressure",
        "pressure-components.json",
        "request-previews",
        "condition-A",
        "condition-B",
        "f2_fresh",
        "f3_fresh",
        "historical_direct_reference_candidates",
    ):
        assert forbidden not in rendered
    assert source_first["authority"]["agent_proxy_is_principal_human"] is False
    assert source_first["authority"]["source_read_is_human_target"] is False
    schema = source_first["agent_proxy_response_schema"]
    assert "source_only_read" in schema["properties"]
    assert "source_only_target" not in render_json(schema)


def test_post_seal_packet_reveals_reference_without_routing_authority() -> None:
    _, post_seal, _, _ = _build()

    assert post_seal["schema_version"] == POST_SEAL_PACKET_SCHEMA_VERSION
    ids = [
        item["model_id"]
        for item in post_seal["historical_direct_reference_candidates"]
    ]
    assert ids == ["signaling", "social-proof"]
    assert post_seal["routing_boundary"] == {
        "routing_input": False,
        "may_change_direct_candidate_ids": False,
        "may_change_generation_packets": False,
        "may_run_graph_or_planner": False,
        "review_output_is_diagnostic_only": True,
    }
    assert (
        post_seal["historical_reference_boundary"]["principal_human_approved_now"]
        is False
    )
    assert (
        post_seal["historical_reference_boundary"][
            "agent_proxy_dispositions_are_observations_not_approvals"
        ]
        is True
    )
    dispositions = post_seal["agent_proxy_response_schema"]["properties"][
        "candidate_reviews"
    ]["items"]["properties"]["disposition"]["enum"]
    assert dispositions == [
        "source_consistent_observation",
        "partly_source_consistent_observation",
        "source_tension_observation",
        "uncertain",
    ]


def test_aliases_are_deterministic_neutral_and_cover_both_conditions() -> None:
    _, _, first_generation, first_sealed = _build()
    _, _, second_generation, second_sealed = _build()

    assert first_generation == second_generation
    assert first_sealed == second_sealed
    assert first_generation["condition_aliases"] == list(CONDITION_ALIASES)
    assert [row["condition_alias"] for row in first_generation["packets"]] == list(
        CONDITION_ALIASES
    )
    assert set(first_sealed["alias_map"]) == set(CONDITION_ALIASES)
    assert {
        row["cell_id"] for row in first_sealed["alias_map"].values()
    } == {F2_CELL_ID, F3_CELL_ID}
    assert {
        row["condition"] for row in first_sealed["alias_map"].values()
    } == {REHEARSAL_DIRECT, REHEARSAL_DIRECT_PLUS_ONE_HOP}
    assert "direct_only" not in render_json(first_generation)
    assert F2_CELL_ID not in render_json(first_generation)
    assert F3_CELL_ID not in render_json(first_generation)


def test_generation_packets_exactly_inherit_messages_and_response_schemas() -> None:
    _, _, generation, sealed = _build()
    previews = {
        F2_CELL_ID: _read_json(F2_PREVIEW_RELPATH),
        F3_CELL_ID: _read_json(F3_PREVIEW_RELPATH),
    }
    packets = {row["condition_alias"]: row for row in generation["packets"]}

    for alias, lineage in sealed["alias_map"].items():
        expected = previews[lineage["cell_id"]]["request_body_projection"]
        actual = packets[alias]["request_body_projection"]
        assert actual["messages"] == expected["messages"]
        assert actual["response_schema"] == expected["response_schema"]
        assert actual["generation"] == expected["generation"]


def test_direct_and_graph_increment_shape_remains_exact() -> None:
    _, post_seal, generation, sealed = _build()
    packets = {row["condition_alias"]: row for row in generation["packets"]}
    by_cell = {
        lineage["cell_id"]: packets[alias]
        for alias, lineage in sealed["alias_map"].items()
    }
    f2_tail = by_cell[F2_CELL_ID]["request_body_projection"]["messages"][2][
        "content"
    ]
    f3_tail = by_cell[F3_CELL_ID]["request_body_projection"]["messages"][2][
        "content"
    ]

    assert "GRAPH_INCREMENT_CANONICAL_JSON:\n[]" in f2_tail
    assert "constitutional_graph_pressure::graph_expansion" not in f2_tail
    assert "constitutional_graph_pressure::graph_expansion" in f3_tail
    assert len(post_seal["historical_direct_reference_candidates"]) == 2


def test_boundaries_preserve_no_human_provider_causal_or_runtime_authority() -> None:
    _, _, generation, sealed = _build()

    assert generation["schema_version"] == GENERATION_PACKETS_SCHEMA_VERSION
    assert sealed["schema_version"] == SEALED_MANIFEST_SCHEMA_VERSION
    boundary = sealed["boundary"]
    assert boundary["repository_provider_api_calls"] == 0
    assert boundary["repository_provider_api_cost_usd"] == 0.0
    assert boundary["repository_provider_execution_authorized"] is False
    assert (
        boundary["codex_agent_only_development_rehearsal_authorized"] is True
    )
    assert boundary["human_review_completed"] is False
    assert boundary["human_authority_created"] is False
    assert boundary["graph_traversal_invoked"] is False
    assert boundary["graph_policy_changed"] is False
    assert boundary["runtime_changed"] is False
    assert boundary["causal_graph_value_identified"] is False
    assert boundary["product_usefulness_validated"] is False
    assert boundary["codex_agent_contexts_predeclared"] == 6
    assert (
        boundary["codex_platform_route_token_and_cost"]
        == "unavailable_to_repository_operator"
    )
    assert (
        boundary["codex_contexts_called_no_ai_calls_or_economically_free"]
        is False
    )
    assert any("not principal-human" in item for item in sealed["non_claims"])
    assert any("not relevance" in item for item in sealed["non_claims"])
    protocol = sealed["codex_context_protocol"]
    assert protocol["allocation"] == {
        "source_first_then_post_seal_followup": 2,
        "isolated_generation": 2,
        "blind_paired_review": 2,
    }
    assert protocol["called_no_ai_calls_or_economically_free"] is False
    assert len(protocol["task_wrapper"]["sha256"]) == 64
    for lineage in sealed["alias_map"].values():
        assert (
            lineage["task_wrapper_sha256"]
            == protocol["task_wrapper"]["sha256"]
        )
        assert (
            lineage["task_wrapper_sha256"]
            != lineage["request_body_projection_sha256"]
        )


def test_sealed_manifest_has_exact_refs_and_generated_hashes() -> None:
    source_first, post_seal, generation, sealed = _build()
    assert set(sealed["input_refs"]) == {
        "contract",
        "authoritative_source",
        "f2_request_preview",
        "f3_request_preview",
        "pressure_components",
        "case_manifest",
    }
    generated = sealed["generated_artifacts"]
    for key, payload in (
        ("source-first-packet", source_first),
        ("post-seal-reference-packet", post_seal),
        ("generation-packets", generation),
    ):
        rendered = render_json(payload).encode("utf-8")
        assert generated[key]["bytes"] == len(rendered)
        assert generated[key]["sha256"] == hashlib.sha256(rendered).hexdigest()


def test_builder_rejects_path_escape() -> None:
    with pytest.raises(
        ProductDeltaGraphIncrementRehearsalError,
        match="escapes the project root",
    ):
        _resolve_repo_path(REPO_ROOT, "../outside.json")
    with pytest.raises(
        ProductDeltaGraphIncrementRehearsalError,
        match="absolute repository path",
    ):
        _resolve_repo_path(REPO_ROOT, "/tmp/outside.json")


def test_checked_in_artifacts_are_exact_builder_output() -> None:
    payloads = _build()
    relpaths = (
        DEFAULT_SOURCE_FIRST_PACKET_RELPATH,
        DEFAULT_POST_SEAL_PACKET_RELPATH,
        DEFAULT_GENERATION_PACKETS_RELPATH,
        DEFAULT_SEALED_MANIFEST_RELPATH,
    )
    for relpath, payload in zip(relpaths, payloads, strict=True):
        assert (REPO_ROOT / relpath).read_text(encoding="utf-8") == render_json(
            payload
        )


def test_artifact_drift_is_reported(tmp_path: Path) -> None:
    # Copy only the declared deterministic input/output surface and alter one
    # generated artifact. Symlink-free copies exercise the same root guard.
    for relpath in (
        DEFAULT_CONTRACT_RELPATH,
        SOURCE_RELPATH,
        F2_PREVIEW_RELPATH,
        F3_PREVIEW_RELPATH,
        "research/consumer-context-role-attribution-case-candidate-2026-07-23/"
        "pressure-components.json",
        "research/consumer-context-role-attribution-case-candidate-2026-07-23/"
        "manifest.json",
        DEFAULT_SOURCE_FIRST_PACKET_RELPATH,
        DEFAULT_POST_SEAL_PACKET_RELPATH,
        DEFAULT_GENERATION_PACKETS_RELPATH,
        DEFAULT_SEALED_MANIFEST_RELPATH,
    ):
        source = REPO_ROOT / relpath
        target = tmp_path / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    (tmp_path / DEFAULT_GENERATION_PACKETS_RELPATH).write_text(
        "{}\n", encoding="utf-8"
    )

    from engine.system_b.product_delta_graph_increment_rehearsal import (
        validate_checked_in_rehearsal,
    )

    errors = validate_checked_in_rehearsal(repo_root=tmp_path)
    assert errors == [
        f"generated artifact drift:{DEFAULT_GENERATION_PACKETS_RELPATH}"
    ]


def test_builder_rejects_authorization_drift(tmp_path: Path) -> None:
    contract = _read_json(DEFAULT_CONTRACT_RELPATH)
    drifted = copy.deepcopy(contract)
    drifted["authorization"]["provider_calls"] = 1
    target = tmp_path / DEFAULT_CONTRACT_RELPATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_json(drifted), encoding="utf-8")

    for relpath in (
        SOURCE_RELPATH,
        F2_PREVIEW_RELPATH,
        F3_PREVIEW_RELPATH,
        "research/consumer-context-role-attribution-case-candidate-2026-07-23/"
        "pressure-components.json",
        "research/consumer-context-role-attribution-case-candidate-2026-07-23/"
        "manifest.json",
    ):
        source = REPO_ROOT / relpath
        copied = tmp_path / relpath
        copied.parent.mkdir(parents=True, exist_ok=True)
        copied.write_bytes(source.read_bytes())

    with pytest.raises(
        ProductDeltaGraphIncrementRehearsalError,
        match="provider calls at zero",
    ):
        build_graph_increment_rehearsal(repo_root=tmp_path)


def test_builder_requires_exact_input_lock_coverage(tmp_path: Path) -> None:
    contract = _read_json(DEFAULT_CONTRACT_RELPATH)
    drifted = copy.deepcopy(contract)
    drifted["input_locks"].pop("f3_request_preview")
    target = tmp_path / DEFAULT_CONTRACT_RELPATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_json(drifted), encoding="utf-8")

    for relpath in (
        SOURCE_RELPATH,
        F2_PREVIEW_RELPATH,
        F3_PREVIEW_RELPATH,
        "research/consumer-context-role-attribution-case-candidate-2026-07-23/"
        "pressure-components.json",
        "research/consumer-context-role-attribution-case-candidate-2026-07-23/"
        "manifest.json",
    ):
        source = REPO_ROOT / relpath
        copied = tmp_path / relpath
        copied.parent.mkdir(parents=True, exist_ok=True)
        copied.write_bytes(source.read_bytes())

    with pytest.raises(
        ProductDeltaGraphIncrementRehearsalError,
        match="exact rehearsal inputs",
    ):
        build_graph_increment_rehearsal(repo_root=tmp_path)


def test_cli_validate_only() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_product_delta_graph_increment_rehearsal.py",
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
    rendered = "".join(render_json(payload) for payload in _build())
    for marker in (
        "/Users/",
        "\\Users\\",
        "BEGIN PRIVATE KEY",
        "client_secret",
        '"api_key"',
        '"password"',
        "sk-proj-",
    ):
        assert marker not in rendered


def test_existing_paired_screen_artifacts_remain_byte_exact() -> None:
    assert validate_checked_in_screen(repo_root=REPO_ROOT) == []
