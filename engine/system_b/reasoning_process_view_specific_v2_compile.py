"""Append-only compiler for relationship-explicit view-specific v2 responses."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .conversation_state_candidates import SourceCatalog
from .reasoning_process_contracts import validate_bounded_view
from .reasoning_process_view_specific import compile_protected_fixture
from .reasoning_process_view_specific_v2 import validate_response_v2
from .reasoning_process_views import canonical_json_bytes, sha256_bytes


COMPILED_SCHEMA = "lolla.reasoning_process_view_specific_v2_compiled.v1"
ADDENDUM_SCHEMA = "lolla.reasoning_process_view_specific_v2_addendum.v1"


def _bridge_record(record: Mapping[str, Any], view_kind: str) -> dict[str, Any]:
    base = {
        "interpretation": record["interpretation"],
        "status": record["status"],
        "auxiliary_observation_ids": record["auxiliary_observation_ids"],
        "limitations": record["limitations"],
    }
    if view_kind == "position_and_decision_trajectory":
        base["position_evidence_ids"] = list(
            dict.fromkeys(
                [
                    *record["starting_state_evidence_ids"],
                    *record["current_position_evidence_ids"],
                ]
            )
        )
        base["qualification_evidence_ids"] = record["qualification_evidence_ids"]
    elif view_kind == "exploration_and_alternatives":
        base["alternative_evidence_ids"] = record["alternative_evidence_ids"]
        base["limitation_evidence_ids"] = record[
            "attached_condition_or_limit_evidence_ids"
        ]
    elif view_kind == "evidence_and_assumption_discipline":
        base["claim_or_input_evidence_ids"] = record["claim_or_input_evidence_ids"]
        base["boundary_evidence_ids"] = record["boundary_evidence_ids"]
    elif view_kind == "uncertainty_and_unresolved_state":
        base["unresolved_evidence_ids"] = record["unresolved_evidence_ids"]
        base["preservation_or_reopen_evidence_ids"] = record[
            "preservation_or_reopen_evidence_ids"
        ]
    else:
        base["challenge_evidence_ids"] = list(
            dict.fromkeys(
                [
                    *record["prior_claim_or_frame_evidence_ids"],
                    *record["challenge_evidence_ids"],
                ]
            )
        )
        base["response_evidence_ids"] = record["response_evidence_ids"]
        base["revision_evidence_ids"] = record["revision_evidence_ids"]
        base["response_type"] = record["response_type"]
    return base


def compile_response_v2(
    *,
    response: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    base_ledger: Mapping[str, Any],
    catalog: SourceCatalog,
    record_identity: str,
    producer_kind: str,
    producer_id: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Compile v2 roles while retaining the existing bounded-view envelope."""

    validated = validate_response_v2(response, wrapper=wrapper)
    view_kind = validated["view_kind"]
    bridge_response = {
        "status": response["status"],
        "records": [_bridge_record(record, view_kind) for record in response["records"]],
        "park_unselected_auxiliary_observations": True,
        "global_limitations": response["global_limitations"],
    }
    compiled = compile_protected_fixture(
        target={"target_id": record_identity, "view_kind": view_kind},
        response=bridge_response,
        wrapper=wrapper,
        base_ledger=base_ledger,
        catalog=catalog,
    )
    authority = "probabilistic_reader" if producer_kind == "model" else "source_reviewer"
    addendum = compiled["fixture_addendum"]
    addendum["schema_version"] = ADDENDUM_SCHEMA
    addendum["status"] = (
        "target_blind_model_v2_addendum"
        if producer_kind == "model"
        else "provider_free_source_review_v2_addendum"
    )
    addendum["boundary"]["v2_relationship_roles_preserved"] = True
    for index, (observation, record, normalized) in enumerate(
        zip(addendum["observations"], response["records"], validated["records"]),
        start=1,
    ):
        raw_record = {
            "record_identity": record_identity,
            "record_index": index,
            "view_kind": view_kind,
            "v2_record": record,
            "v2_role_source_span_ids": normalized["role_source_span_ids"],
        }
        observation["raw_record"] = raw_record
        observation["raw_record_sha256"] = "sha256:" + sha256_bytes(
            canonical_json_bytes(raw_record)
        )
        observation["source_span_ids"] = normalized["source_span_ids"]
        observation["family_projection_status"] = (
            "view_specific_v2_model_interpretation"
            if producer_kind == "model"
            else "view_specific_v2_source_review_fixture"
        )
        observation["provenance"] = {
            "producer_kind": producer_kind,
            "producer_id": producer_id,
            "call_id": (call_metadata or {}).get("call_id", ""),
            "model": (call_metadata or {}).get("model", ""),
            "prompt_sha256": (call_metadata or {}).get("prompt_sha256", ""),
        }
        observation["state_history"][0]["actor"] = authority
        observation["state_history"][0]["reason"] = (
            "target-blind relationship-explicit model proposal"
            if producer_kind == "model"
            else "prospectively source-reviewed relationship fixture"
        )
        observation["terminal_reason"] = (
            "v2 relationship roles and stable aliases passed deterministic validation"
        )
    addendum_sha = sha256_bytes(canonical_json_bytes(addendum))
    combined = [*base_ledger["observations"], *addendum["observations"]]
    manifest = {
        "case_id": wrapper["reader_packet"]["case_id"],
        "view_kind": view_kind,
        "base_ledger_sha256": compiled["combined_manifest"]["base_ledger_sha256"],
        "fixture_addendum_sha256": "sha256:" + addendum_sha,
        "observation_ids": [item["observation_id"] for item in combined],
    }
    manifest_sha = sha256_bytes(canonical_json_bytes(manifest))
    view = compiled["view"]
    view["source_ledger_sha256"] = "sha256:" + manifest_sha
    for disposition in view["dispositions"]:
        disposition["authority"] = authority
    validation = validate_bounded_view(
        view,
        known_ledger_observation_ids=[item["observation_id"] for item in combined],
        known_span_ids=catalog.by_id(),
        expected_ledger_sha256="sha256:" + manifest_sha,
    )
    return {
        "schema_version": COMPILED_SCHEMA,
        "status": "view_specific_v2_response_compiled",
        "model_backed": producer_kind == "model",
        "model_response_changed": False,
        "model_addendum": addendum,
        "model_addendum_sha256": addendum_sha,
        "combined_manifest": manifest,
        "combined_manifest_sha256": manifest_sha,
        "view": view,
        "view_validation": validation,
        "boundary": {
            "v2_raw_relationship_roles_preserved": True,
            "semantic_adequacy_validated": False,
            "phase1_ledger_modified": False,
            "direct_graph_routing_allowed": False,
        },
    }
