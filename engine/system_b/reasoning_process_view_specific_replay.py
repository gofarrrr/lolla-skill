"""Deterministic replay repair for view-specific model-response custody.

The live probe used ``model`` as a bounded-view disposition authority, while
the frozen Phase-0 contract names that authority ``probabilistic_reader``.
This module replays preserved, already alias-valid payloads without changing
their content or making another provider call.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .conversation_state_candidates import SourceCatalog
from .reasoning_process_contracts import validate_bounded_view
from .reasoning_process_view_specific import compile_protected_fixture
from .reasoning_process_views import canonical_json_bytes, sha256_bytes


MODEL_ADDENDUM_SCHEMA = "lolla.reasoning_process_view_specific_model_addendum.v1"
REPLAY_SCHEMA = "lolla.reasoning_process_view_specific_replay.v1"


def compile_preserved_model_response(
    *,
    response: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    base_ledger: Mapping[str, Any],
    catalog: SourceCatalog,
    call_metadata: Mapping[str, str],
) -> dict[str, Any]:
    """Compile one preserved payload with the contract's authority vocabulary."""

    target = {
        "target_id": f"replay-{call_metadata['call_id']}",
        "view_kind": wrapper["reader_packet"]["view_kind"],
    }
    compiled = compile_protected_fixture(
        target=target,
        response=response,
        wrapper=wrapper,
        base_ledger=base_ledger,
        catalog=catalog,
    )
    addendum = compiled["fixture_addendum"]
    addendum["schema_version"] = MODEL_ADDENDUM_SCHEMA
    addendum["status"] = "replayed_target_blind_model_addendum"
    addendum["boundary"]["model_output_target_blind"] = True
    for observation in addendum["observations"]:
        observation["family_projection_status"] = "view_specific_model_interpretation"
        observation["source_artifact_id"] = "view-specific-model-probe"
        observation["provenance"] = {
            "producer_kind": "model",
            "producer_id": call_metadata["requested_model"],
            "call_id": call_metadata["call_id"],
            "model": call_metadata["served_model"],
            "prompt_sha256": call_metadata["prompt_sha256"],
        }
        observation["state_history"][0] = {
            "state": "proposed",
            "reason": "target-blind view-specific model proposal",
            "actor": "probabilistic_reader",
        }
        observation["terminal_reason"] = (
            "preserved model interpretation passed typed stable-alias validation"
        )

    addendum_sha = sha256_bytes(canonical_json_bytes(addendum))
    combined = [*base_ledger["observations"], *addendum["observations"]]
    manifest = {
        "case_id": wrapper["reader_packet"]["case_id"],
        "view_kind": wrapper["reader_packet"]["view_kind"],
        "base_ledger_sha256": compiled["combined_manifest"]["base_ledger_sha256"],
        "fixture_addendum_sha256": "sha256:" + addendum_sha,
        "observation_ids": [item["observation_id"] for item in combined],
    }
    manifest_sha = sha256_bytes(canonical_json_bytes(manifest))
    view = compiled["view"]
    view["source_ledger_sha256"] = "sha256:" + manifest_sha
    for disposition in view["dispositions"]:
        disposition["authority"] = "probabilistic_reader"
    validation = validate_bounded_view(
        view,
        known_ledger_observation_ids=[item["observation_id"] for item in combined],
        known_span_ids=catalog.by_id(),
        expected_ledger_sha256="sha256:" + manifest_sha,
    )
    return {
        "schema_version": REPLAY_SCHEMA,
        "status": "preserved_model_response_compiled",
        "replay_reason": (
            "Normalize compiler authority from the implementation-only label "
            "model to the frozen contract label probabilistic_reader."
        ),
        "response_changed": False,
        "provider_calls": 0,
        "model_addendum": addendum,
        "model_addendum_sha256": addendum_sha,
        "combined_manifest": manifest,
        "combined_manifest_sha256": manifest_sha,
        "view": view,
        "view_validation": validation,
        "boundary": {
            "semantic_adequacy_validated": False,
            "response_healed": False,
            "provider_retry_performed": False,
            "phase1_ledger_modified": False,
            "graph_routing_allowed": False,
        },
    }
