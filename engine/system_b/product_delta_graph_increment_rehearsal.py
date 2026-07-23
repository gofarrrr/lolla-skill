"""Case-specific Product Delta packaging for a direct-vs-one-hop rehearsal.

This module freezes checked-in-safe source-first, post-seal reference-review,
and neutrally aliased generation packets derived from the existing F2/F3
previews. Those previews are lineage and payload sources, not realized F2/F3
outputs. The module does not call a provider, run the graph, change routing,
fill a human field, execute a generation request, or judge graph value.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


CONTRACT_SCHEMA_VERSION = (
    "lolla.product_delta_agent_graph_increment_rehearsal_contract.v1"
)
SOURCE_FIRST_PACKET_SCHEMA_VERSION = (
    "lolla.product_delta_agent_source_first_packet.v1"
)
POST_SEAL_PACKET_SCHEMA_VERSION = (
    "lolla.product_delta_agent_post_seal_reference_packet.v1"
)
GENERATION_PACKETS_SCHEMA_VERSION = (
    "lolla.product_delta_agent_graph_increment_generation_packets.v1"
)
SEALED_MANIFEST_SCHEMA_VERSION = (
    "lolla.product_delta_agent_graph_increment_sealed_manifest.v1"
)

REHEARSAL_ID = "agent-only-graph-increment-rehearsal-2026-07-23"
BLINDING_NAMESPACE = "lolla-product-delta-graph-increment-rehearsal-v1"
DEFAULT_CONTRACT_RELPATH = (
    "docs/evals/lolla-agent-only-graph-increment-rehearsal-contract-v1.json"
)
CASE_DIR_RELPATH = (
    "research/consumer-context-role-attribution-case-candidate-2026-07-23"
)
SOURCE_RELPATH = (
    "research/independent-phase5-cases-2026-07-12/useful-pressure-case.txt"
)
F2_PREVIEW_RELPATH = (
    f"{CASE_DIR_RELPATH}/request-previews/"
    "f2_fresh_human_controlled_fact_free_direct_only.json"
)
F3_PREVIEW_RELPATH = (
    f"{CASE_DIR_RELPATH}/request-previews/"
    "f3_fresh_human_controlled_fact_free_plus_current_graph.json"
)
PRESSURE_COMPONENTS_RELPATH = f"{CASE_DIR_RELPATH}/pressure-components.json"
CASE_MANIFEST_RELPATH = f"{CASE_DIR_RELPATH}/manifest.json"
DEFAULT_OUTPUT_DIR_RELPATH = (
    "research/agent-only-graph-increment-rehearsal-2026-07-23"
)
DEFAULT_SOURCE_FIRST_PACKET_RELPATH = (
    f"{DEFAULT_OUTPUT_DIR_RELPATH}/source-first-packet.json"
)
DEFAULT_POST_SEAL_PACKET_RELPATH = (
    f"{DEFAULT_OUTPUT_DIR_RELPATH}/post-seal-reference-packet.json"
)
DEFAULT_GENERATION_PACKETS_RELPATH = (
    f"{DEFAULT_OUTPUT_DIR_RELPATH}/generation-packets.json"
)
DEFAULT_SEALED_MANIFEST_RELPATH = (
    f"{DEFAULT_OUTPUT_DIR_RELPATH}/sealed-manifest.json"
)

F2_CELL_ID = "f2_fresh_human_controlled_fact_free_direct_only"
F3_CELL_ID = "f3_fresh_human_controlled_fact_free_plus_current_graph"
REHEARSAL_DIRECT = "rehearsal_direct"
REHEARSAL_DIRECT_PLUS_ONE_HOP = (
    "rehearsal_direct_plus_current_one_hop"
)
CONDITION_ALIASES = ("condition-A", "condition-B")
GENERATION_TASK_WRAPPER = (
    "Run one isolated Codex development-rehearsal task. The supplied packet is "
    "derived from a checked-in provider-neutral preview but is not exact provider "
    "execution of F2 or F3: ambient platform system and developer context remains "
    "present, and the underlying model route, token usage, and platform cost are "
    "unavailable to the repository operator. Follow the embedded message array as "
    "the semantic instruction, return only one JSON object conforming to the "
    "embedded response schema, make no repository provider API call, and preserve "
    "the first terminal result without retry, fallback, or response healing."
)

BOUNDARY = {
    "repository_provider_api_calls": 0,
    "repository_provider_api_cost_usd": 0.0,
    "repository_provider_execution_authorized": False,
    "repository_provider_request_executed": False,
    "codex_agent_only_development_rehearsal_authorized": True,
    "codex_agent_contexts_predeclared": 6,
    "codex_platform_route_token_and_cost": "unavailable_to_repository_operator",
    "codex_contexts_called_no_ai_calls_or_economically_free": False,
    "ambient_platform_system_and_developer_context_present": True,
    "private_archives_read": False,
    "human_review_completed": False,
    "human_authority_created": False,
    "runtime_invoked": False,
    "graph_traversal_invoked": False,
    "graph_policy_changed": False,
    "runtime_changed": False,
    "routing_changed_by_post_seal_review": False,
    "causal_graph_value_identified": False,
    "answer_quality_scored": False,
    "product_usefulness_validated": False,
}

NON_CLAIMS = (
    "agent proxy output is not principal-human evidence",
    "historical source review is not current human approval",
    "a frozen request packet is not provider execution authorization",
    "Codex agent contexts are not no-AI calls or known to be economically free",
    "one output per condition would remain a single-draw case diagnostic",
    "the pair cannot establish expected causal effect or graph usefulness",
    "graph reachability is not relevance, truth, importance, or causation",
    "post-seal reference review cannot change deterministic routing",
    "this offline package does not change the live skill, graph, or runtime",
)

SECRET_MARKERS = (
    "/Users/",
    "\\Users\\",
    "BEGIN PRIVATE KEY",
    "client_secret",
    '"api_key"',
    '"password"',
    "sk-proj-",
)


class ProductDeltaGraphIncrementRehearsalError(ValueError):
    """Sanitized deterministic input or custody failure."""


def build_graph_increment_rehearsal(
    *, repo_root: Path | str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Build four rehearsal inputs without writing or calling a provider API."""

    root = Path(repo_root).resolve()
    contract, contract_ref = _read_json_ref(root, DEFAULT_CONTRACT_RELPATH)
    if contract.get("schema_version") != CONTRACT_SCHEMA_VERSION:
        raise ProductDeltaGraphIncrementRehearsalError(
            "graph-increment rehearsal contract schema version mismatch"
        )
    _validate_contract_boundary(contract)

    source, source_ref = _read_text_ref(root, SOURCE_RELPATH)
    f2, f2_ref = _read_json_ref(root, F2_PREVIEW_RELPATH)
    f3, f3_ref = _read_json_ref(root, F3_PREVIEW_RELPATH)
    pressure, pressure_ref = _read_json_ref(root, PRESSURE_COMPONENTS_RELPATH)
    case_manifest, case_manifest_ref = _read_json_ref(root, CASE_MANIFEST_RELPATH)
    _validate_declared_input_locks(
        contract=contract,
        refs={
            "source": source_ref,
            "f2_request_preview": f2_ref,
            "f3_request_preview": f3_ref,
            "pressure_components": pressure_ref,
            "case_manifest": case_manifest_ref,
        },
    )
    _validate_case_inputs(
        source=source,
        f2=f2,
        f3=f3,
        pressure=pressure,
        case_manifest=case_manifest,
    )

    source_schema = _agent_proxy_schema(contract, "source_first")
    post_seal_schema = _agent_proxy_schema(contract, "post_seal_reference")
    source_first = _build_source_first_packet(
        source=source,
        source_ref=source_ref,
        response_schema=source_schema,
    )
    source_first_rendered = render_json(source_first)

    direct_component = _required_mapping(pressure, "direct_component")
    post_seal = _build_post_seal_packet(
        source_first_sha256=_sha256_text(source_first_rendered),
        direct_component=direct_component,
        response_schema=post_seal_schema,
    )
    generation, alias_map = _build_generation_packets(
        source_sha256=source_ref["sha256"],
        contract_sha256=contract_ref["sha256"],
        f2=f2,
        f2_ref=f2_ref,
        f3=f3,
        f3_ref=f3_ref,
    )

    artifact_renders = {
        DEFAULT_SOURCE_FIRST_PACKET_RELPATH: source_first_rendered,
        DEFAULT_POST_SEAL_PACKET_RELPATH: render_json(post_seal),
        DEFAULT_GENERATION_PACKETS_RELPATH: render_json(generation),
    }
    sealed = {
        "schema_version": SEALED_MANIFEST_SCHEMA_VERSION,
        "rehearsal_id": REHEARSAL_ID,
        "status": (
            "codex_development_rehearsal_contract_frozen_"
            "repository_provider_execution_not_authorized"
        ),
        "handling": {
            "show_to_source_first_proxy_before_source_response_is_frozen": False,
            "show_to_generation_consumers": False,
            "reveal_condition_lineage_only_after_outputs_and_reviews_are_frozen": True,
            "post_seal_reference_review_changes_routing": False,
            "agent_proxy_is_principal_human": False,
        },
        "boundary": dict(BOUNDARY),
        "input_refs": {
            "contract": contract_ref,
            "authoritative_source": source_ref,
            "f2_request_preview": f2_ref,
            "f3_request_preview": f3_ref,
            "pressure_components": pressure_ref,
            "case_manifest": case_manifest_ref,
        },
        "generated_artifacts": {
            relpath.rsplit("/", 1)[-1].removesuffix(".json"): {
                "path": relpath,
                "sha256": _sha256_text(rendered),
                "bytes": len(rendered.encode("utf-8")),
            }
            for relpath, rendered in artifact_renders.items()
        },
        "alias_map": alias_map,
        "alias_policy": {
            "namespace": BLINDING_NAMESPACE,
            "deterministic": True,
            "neutral_labels": list(CONDITION_ALIASES),
            "both_conditions_present": True,
            "lineage_is_not_in_generation_packets": True,
        },
        "condition_boundary": {
            "rehearsal_conditions": [
                REHEARSAL_DIRECT,
                REHEARSAL_DIRECT_PLUS_ONE_HOP,
            ],
            "preview_lineage_only": {
                REHEARSAL_DIRECT: F2_CELL_ID,
                REHEARSAL_DIRECT_PLUS_ONE_HOP: F3_CELL_ID,
            },
            "rehearsal_outputs_complete_f2_or_f3": False,
            "allowed_difference": (
                "The direct-plus-current-one-hop rehearsal derives its semantic "
                "payload from the existing F3 preview while the direct rehearsal "
                "derives its semantic payload from F2. These previews are lineage "
                "and exact payload sources, not realized F2/F3 provider outputs. "
                "The builder edits neither message array nor response schema."
            ),
            "f2_f3_direct_component_identity_preserved": True,
            "graph_increment_is_existing_outgoing_one_hop_payload": True,
            "graph_traversal_performed_by_rehearsal": False,
        },
        "codex_context_protocol": {
            "predeclared_context_count": 6,
            "allocation": {
                "source_first_then_post_seal_followup": 2,
                "isolated_generation": 2,
                "blind_paired_review": 2,
            },
            "ambient_platform_system_and_developer_context_present": True,
            "exact_three_message_provider_envelope_claimed": False,
            "underlying_platform_model_route_token_and_cost": (
                "unavailable_to_repository_operator"
            ),
            "called_no_ai_calls_or_economically_free": False,
            "repository_provider_api_call": False,
            "task_wrapper": {
                "text": GENERATION_TASK_WRAPPER,
                "sha256": _sha256_text(GENERATION_TASK_WRAPPER),
                "separate_from_preview_hash": True,
            },
        },
        "non_claims": list(NON_CLAIMS),
    }
    _assert_safe_generated(
        {
            "source_first": source_first,
            "post_seal": post_seal,
            "generation": generation,
            "sealed": sealed,
        }
    )
    return source_first, post_seal, generation, sealed


def render_json(payload: Mapping[str, Any]) -> str:
    """Render a stable checked-in JSON representation."""

    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_checked_in_rehearsal(*, repo_root: Path | str) -> None:
    """Write deterministic rehearsal inputs after explicit operator invocation."""

    root = Path(repo_root).resolve()
    payloads = build_graph_increment_rehearsal(repo_root=root)
    for relpath, payload in zip(_output_relpaths(), payloads, strict=True):
        path = _resolve_repo_path(root, relpath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_json(payload), encoding="utf-8")


def validate_checked_in_rehearsal(*, repo_root: Path | str) -> list[str]:
    """Return deterministic missing/drift messages for generated artifacts."""

    root = Path(repo_root).resolve()
    payloads = build_graph_increment_rehearsal(repo_root=root)
    errors: list[str] = []
    for relpath, payload in zip(_output_relpaths(), payloads, strict=True):
        path = _resolve_repo_path(root, relpath)
        try:
            actual = path.read_text(encoding="utf-8")
        except OSError:
            errors.append(f"missing generated artifact:{relpath}")
            continue
        if actual != render_json(payload):
            errors.append(f"generated artifact drift:{relpath}")
    return errors


def _output_relpaths() -> tuple[str, ...]:
    return (
        DEFAULT_SOURCE_FIRST_PACKET_RELPATH,
        DEFAULT_POST_SEAL_PACKET_RELPATH,
        DEFAULT_GENERATION_PACKETS_RELPATH,
        DEFAULT_SEALED_MANIFEST_RELPATH,
    )


def _build_source_first_packet(
    *,
    source: str,
    source_ref: Mapping[str, Any],
    response_schema: Mapping[str, Any],
) -> dict[str, Any]:
    # Deliberately no contract, candidate, portfolio, prior-output, request,
    # condition, or lineage references appear in this packet.
    return {
        "schema_version": SOURCE_FIRST_PACKET_SCHEMA_VERSION,
        "packet_id": "agent-only-source-first-proxy-2026-07-23",
        "status": "source_only_agent_proxy_packet",
        "evidence_class": (
            "checked_in_safe_complete_source_for_agent_proxy_not_human_evidence"
        ),
        "instruction_order": [
            "Read the complete supplied source before forming the response.",
            "Use only the supplied source words.",
            "Preserve uncertainty, unresolved matters, and strong existing reasoning.",
            (
                "Do not infer missing private context, select an answer, or "
                "create action authority."
            ),
            "Return only the declared structured response.",
        ],
        "authoritative_source": {
            "coverage": "complete_checked_in_conversation",
            "content": source,
            "sha256": source_ref["sha256"],
            "utf8_bytes": source_ref["bytes"],
            "omissions": [],
        },
        "agent_proxy_response_schema": copy.deepcopy(dict(response_schema)),
        "authority": {
            "agent_proxy_is_principal_human": False,
            "source_read_is_human_target": False,
            "semantic_correctness_certified": False,
            "human_usefulness_validated": False,
            "action_authority_created": False,
        },
        "non_claims": [
            "not principal-human evidence",
            "not ground truth",
            "not answer-quality certification",
            "not product-usefulness evidence",
            "not action authority",
        ],
    }


def _build_post_seal_packet(
    *,
    source_first_sha256: str,
    direct_component: Mapping[str, Any],
    response_schema: Mapping[str, Any],
) -> dict[str, Any]:
    items = _required_sequence(direct_component, "items")
    return {
        "schema_version": POST_SEAL_PACKET_SCHEMA_VERSION,
        "rehearsal_id": REHEARSAL_ID,
        "status": "post_source_seal_reference_review_only",
        "evidence_class": (
            "historical_direct_reference_candidate_review_by_agent_proxy_"
            "not_human_approval"
        ),
        "open_only_after": {
            "source_first_proxy_response_frozen": True,
            "source_first_packet_sha256": source_first_sha256,
        },
        "historical_direct_reference_candidates": copy.deepcopy(list(items)),
        "historical_reference_boundary": {
            "source_reviewed_historically": True,
            "principal_human_approved_now": False,
            "agent_proxy_dispositions_are_observations_not_approvals": True,
            "is_oracle": False,
        },
        "routing_boundary": {
            "routing_input": False,
            "may_change_direct_candidate_ids": False,
            "may_change_generation_packets": False,
            "may_run_graph_or_planner": False,
            "review_output_is_diagnostic_only": True,
        },
        "agent_proxy_response_schema": copy.deepcopy(dict(response_schema)),
        "non_claims": [
            "not principal-human review",
            "not current human approval",
            "not a routing instruction",
            "not relevance or usefulness proof",
            "not permission to edit the frozen generation pair",
        ],
    }


def _build_generation_packets(
    *,
    source_sha256: str,
    contract_sha256: str,
    f2: Mapping[str, Any],
    f2_ref: Mapping[str, Any],
    f3: Mapping[str, Any],
    f3_ref: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    seed = _sha256_text(
        "|".join(
            (
                BLINDING_NAMESPACE,
                source_sha256,
                contract_sha256,
                str(f2_ref["sha256"]),
                str(f3_ref["sha256"]),
            )
        )
    )
    direct_alias, graph_alias = (
        ("condition-B", "condition-A")
        if bytes.fromhex(seed)[0] % 2
        else ("condition-A", "condition-B")
    )
    by_alias = {
        direct_alias: (F2_CELL_ID, REHEARSAL_DIRECT, f2, f2_ref),
        graph_alias: (
            F3_CELL_ID,
            REHEARSAL_DIRECT_PLUS_ONE_HOP,
            f3,
            f3_ref,
        ),
    }
    packets: list[dict[str, Any]] = []
    alias_map: dict[str, Any] = {}
    for alias in CONDITION_ALIASES:
        cell_id, condition, preview, preview_ref = by_alias[alias]
        request = _required_mapping(preview, "request_body_projection")
        packets.append(
            {
                "condition_alias": alias,
                "request_body_projection": copy.deepcopy(dict(request)),
                "inheritance": {
                    "messages_inherited_byte_for_byte_as_json_values": True,
                    "response_schema_inherited_byte_for_byte_as_json_value": True,
                    "generation_settings_inherited_without_repair": True,
                    "request_body_projection_sha256": _sha256_json_value(request),
                    "preview_is_lineage_and_payload_source_not_realized_output": True,
                },
                "codex_task_wrapper": {
                    "text": GENERATION_TASK_WRAPPER,
                    "sha256": _sha256_text(GENERATION_TASK_WRAPPER),
                    "hash_is_separate_from_preview_and_request_hashes": True,
                    "ambient_platform_context_remains_present": True,
                },
                "execution": {
                    "codex_agent_development_rehearsal_authorized": True,
                    "performed": False,
                    "repository_provider_api_calls": 0,
                    "repository_provider_execution_authorized": False,
                    "underlying_platform_model_route_token_and_cost": (
                        "unavailable_to_repository_operator"
                    ),
                    "called_no_ai_calls_or_economically_free": False,
                    "retry_or_fallback_authorized": False,
                },
            }
        )
        alias_map[alias] = {
            "cell_id": cell_id,
            "condition": condition,
            "source_preview_ref": copy.deepcopy(dict(preview_ref)),
            "request_body_projection_sha256": _sha256_json_value(request),
            "messages_sha256": _sha256_json_value(
                _required_sequence(request, "messages")
            ),
            "response_schema_sha256": _sha256_json_value(
                _required_mapping(request, "response_schema")
            ),
            "task_wrapper_sha256": _sha256_text(GENERATION_TASK_WRAPPER),
        }
    payload = {
        "schema_version": GENERATION_PACKETS_SCHEMA_VERSION,
        "rehearsal_id": REHEARSAL_ID,
        "status": (
            "frozen_neutral_aliases_codex_rehearsal_authorized_"
            "repository_provider_execution_not_authorized"
        ),
        "packet_count": 2,
        "condition_aliases": list(CONDITION_ALIASES),
        "packets": packets,
        "blinding": {
            "deterministic": True,
            "seed_sha256": seed,
            "lineage_in_this_artifact": False,
            "alias_meaning_available_only_in_sealed_manifest": True,
        },
        "boundary": {
            "repository_provider_api_calls": 0,
            "repository_provider_execution_authorized": False,
            "codex_agent_only_development_rehearsal_authorized": True,
            "runtime_invoked": False,
            "graph_traversal_invoked": False,
            "messages_or_response_schemas_modified": False,
            "single_draw_causal_claim_authorized": False,
            "rehearsal_outputs_complete_f2_or_f3": False,
        },
        "non_claims": list(NON_CLAIMS),
    }
    return payload, alias_map


def _validate_case_inputs(
    *,
    source: str,
    f2: Mapping[str, Any],
    f3: Mapping[str, Any],
    pressure: Mapping[str, Any],
    case_manifest: Mapping[str, Any],
) -> None:
    if not source.strip():
        raise ProductDeltaGraphIncrementRehearsalError(
            "authoritative source is empty"
        )
    if f2.get("cell_id") != F2_CELL_ID or f3.get("cell_id") != F3_CELL_ID:
        raise ProductDeltaGraphIncrementRehearsalError(
            "F2 or F3 request preview identity mismatch"
        )
    for preview in (f2, f3):
        if preview.get("provider_execution_authorized") is not False:
            raise ProductDeltaGraphIncrementRehearsalError(
                "request preview unexpectedly authorizes provider execution"
            )
        request = _required_mapping(preview, "request_body_projection")
        messages = _required_sequence(request, "messages")
        _required_mapping(request, "response_schema")
        if len(messages) != 3:
            raise ProductDeltaGraphIncrementRehearsalError(
                "request preview message count drifted"
            )

    direct = _required_mapping(pressure, "direct_component")
    graph_increment = _required_mapping(pressure, "graph_increment")
    direct_items = _required_sequence(direct, "items")
    graph_items = _required_sequence(graph_increment, "items")
    if not direct_items or not graph_items:
        raise ProductDeltaGraphIncrementRehearsalError(
            "direct component or graph increment is empty"
        )
    for item in direct_items:
        row = _as_mapping(item, "direct component item")
        if row.get("candidate_origin") != "direct_seed":
            raise ProductDeltaGraphIncrementRehearsalError(
                "direct component contains a non-direct item"
            )
        content = _required_mapping(row, "pressure_content")
        if "graph_path" in content:
            raise ProductDeltaGraphIncrementRehearsalError(
                "direct component unexpectedly contains a graph path"
            )
    for item in graph_items:
        row = _as_mapping(item, "graph increment item")
        if row.get("candidate_origin") != "graph_expansion":
            raise ProductDeltaGraphIncrementRehearsalError(
                "graph increment contains a non-expansion item"
            )
        _required_mapping(_required_mapping(row, "pressure_content"), "graph_path")

    direct_json = _required_text(direct, "canonical_json")
    graph_json = _required_text(graph_increment, "canonical_json")
    f2_tail = _message_content(f2, index=2)
    f3_tail = _message_content(f3, index=2)
    if direct_json not in f2_tail or direct_json not in f3_tail:
        raise ProductDeltaGraphIncrementRehearsalError(
            "F2/F3 direct component identity drifted"
        )
    if "GRAPH_INCREMENT_CANONICAL_JSON:\n[]" not in f2_tail:
        raise ProductDeltaGraphIncrementRehearsalError(
            "F2 is no longer the direct-only request"
        )
    if graph_json not in f3_tail:
        raise ProductDeltaGraphIncrementRehearsalError(
            "F3 no longer contains the declared graph increment"
        )

    manifest_artifacts = case_manifest.get("artifacts")
    if not isinstance(manifest_artifacts, list):
        raise ProductDeltaGraphIncrementRehearsalError(
            "case manifest is missing artifact custody"
        )
    expected_paths = {
        F2_PREVIEW_RELPATH,
        F3_PREVIEW_RELPATH,
        PRESSURE_COMPONENTS_RELPATH,
    }
    declared_paths = {
        str(item.get("path"))
        for item in manifest_artifacts
        if isinstance(item, Mapping)
    }
    if not expected_paths.issubset(declared_paths):
        raise ProductDeltaGraphIncrementRehearsalError(
            "case manifest does not declare required rehearsal inputs"
        )


def _message_content(preview: Mapping[str, Any], *, index: int) -> str:
    request = _required_mapping(preview, "request_body_projection")
    messages = _required_sequence(request, "messages")
    if index >= len(messages):
        raise ProductDeltaGraphIncrementRehearsalError(
            "request preview message index is missing"
        )
    return _required_text(_as_mapping(messages[index], "request message"), "content")


def _validate_contract_boundary(contract: Mapping[str, Any]) -> None:
    authorization = contract.get("authorization")
    if not isinstance(authorization, Mapping):
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract is missing authorization boundary"
        )
    if authorization.get("provider_calls") != 0:
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract does not freeze provider calls at zero"
        )
    if authorization.get("provider_cost_usd") != 0.0:
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract does not freeze provider cost at zero"
        )
    for key in (
        "private_archive_inspection",
        "principal_human_review",
        "human_usefulness_claim",
        "runtime_change",
        "graph_policy_change",
        "skill_change",
        "provider_backed_execution",
    ):
        if authorization.get(key) is not False:
            raise ProductDeltaGraphIncrementRehearsalError(
                f"contract unexpectedly authorizes:{key}"
            )
    if authorization.get("codex_agent_only_rehearsal") is not True:
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract does not authorize the bounded Codex rehearsal"
        )
    scope = contract.get("scope")
    if not isinstance(scope, Mapping):
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract is missing rehearsal scope"
        )
    if scope.get("included_comparison") != (
        "rehearsal_direct_versus_rehearsal_direct_plus_current_one_hop"
    ):
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract rehearsal comparison drifted"
        )
    if scope.get("preview_lineage_only") != {
        REHEARSAL_DIRECT: F2_CELL_ID,
        REHEARSAL_DIRECT_PLUS_ONE_HOP: F3_CELL_ID,
    }:
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract rehearsal lineage drifted"
        )
    if scope.get("rehearsal_outputs_complete_f2_or_f3") is not False:
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract falsely promotes rehearsal outputs to F2/F3"
        )
    owners = contract.get("existing_owners_reused")
    if not isinstance(owners, Mapping):
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract is missing existing-owner custody"
        )
    expected = {
        "authoritative_source": SOURCE_RELPATH,
        "case_candidate_manifest": CASE_MANIFEST_RELPATH,
        "pressure_components": PRESSURE_COMPONENTS_RELPATH,
        "direct_only_request_preview": F2_PREVIEW_RELPATH,
        "direct_plus_graph_request_preview": F3_PREVIEW_RELPATH,
    }
    if any(owners.get(key) != value for key, value in expected.items()):
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract existing-owner paths drifted"
        )
    generation = contract.get("generation_rehearsal")
    if not isinstance(generation, Mapping):
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract is missing generation rehearsal boundary"
        )
    if generation.get("predeclared_fresh_agent_context_count") != 6:
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract Codex context count drifted"
        )
    if (
        generation.get("underlying_platform_model_route_token_and_cost_custody")
        != "unavailable_to_repository_operator"
    ):
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract platform-cost custody drifted"
        )
    if (
        generation.get("do_not_call_agent_sessions_no_ai_calls_or_economically_free")
        is not True
    ):
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract economic nonclaim drifted"
        )
    _validate_agent_proxy_schema_boundaries(contract)
    post_seal = contract.get("post_seal_reference_review")
    if not isinstance(post_seal, Mapping):
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract is missing post-seal observation boundary"
        )
    if post_seal.get("approval_or_rejection_authority") is not False:
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract gives the agent proxy approval authority"
        )
    allowed = post_seal.get("allowed_dispositions")
    if allowed != [
        "source_consistent_observation",
        "partly_source_consistent_observation",
        "source_tension_observation",
        "uncertain",
    ]:
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract post-seal observation vocabulary drifted"
        )


def _validate_agent_proxy_schema_boundaries(contract: Mapping[str, Any]) -> None:
    source_schema = _agent_proxy_schema(contract, "source_first")
    source_required = source_schema.get("required")
    required_source_fields = {
        "terminal_status",
        "source_read_complete",
        "source_only_read",
        "terminal_receipt",
    }
    if not isinstance(source_required, list) or not required_source_fields.issubset(
        set(source_required)
    ):
        raise ProductDeltaGraphIncrementRehearsalError(
            "source-first schema does not preserve terminal-state custody"
        )
    source_properties = _required_mapping(source_schema, "properties")
    terminal_status = _required_mapping(source_properties, "terminal_status")
    if terminal_status.get("enum") != [
        "complete",
        "completed_zero",
        "partial",
        "failed",
        "missing",
    ]:
        raise ProductDeltaGraphIncrementRehearsalError(
            "source-first terminal-state vocabulary drifted"
        )
    if _required_mapping(source_properties, "source_read_complete").get("type") != (
        "boolean"
    ):
        raise ProductDeltaGraphIncrementRehearsalError(
            "source-first completion flag is not state-dependent"
        )
    receipt = _required_mapping(source_properties, "terminal_receipt")
    receipt_required = receipt.get("required")
    if not isinstance(receipt_required, list) or {
        "first_terminal_result_preserved",
        "source_only_visibility_preserved",
        "post_seal_stage_eligible",
        "state_reason",
    } != set(receipt_required):
        raise ProductDeltaGraphIncrementRehearsalError(
            "source-first terminal receipt drifted"
        )
    state_conditions: set[str] = set()
    for raw_rule in _required_sequence(source_schema, "allOf"):
        rule = _as_mapping(raw_rule, "source-first terminal-state rule")
        condition = _required_mapping(_required_mapping(rule, "if"), "properties")
        status_condition = _required_mapping(condition, "terminal_status")
        if isinstance(status_condition.get("const"), str):
            state_conditions.add(str(status_condition["const"]))
        elif isinstance(status_condition.get("enum"), list):
            state_conditions.update(str(item) for item in status_condition["enum"])
    if state_conditions != {
        "complete",
        "completed_zero",
        "partial",
        "failed",
        "missing",
    }:
        raise ProductDeltaGraphIncrementRehearsalError(
            "source-first terminal-state receipt conditions drifted"
        )

    post_seal_schema = _agent_proxy_schema(contract, "post_seal_reference")
    post_properties = _required_mapping(post_seal_schema, "properties")
    candidate_reviews = _required_mapping(post_properties, "candidate_reviews")
    contains_ids: list[str] = []
    for raw_rule in _required_sequence(candidate_reviews, "allOf"):
        rule = _as_mapping(raw_rule, "candidate review uniqueness rule")
        if rule.get("minContains") != 1 or rule.get("maxContains") != 1:
            raise ProductDeltaGraphIncrementRehearsalError(
                "candidate review exact-cardinality rule drifted"
            )
        contains = _required_mapping(rule, "contains")
        properties = _required_mapping(contains, "properties")
        model_id = _required_mapping(properties, "model_id").get("const")
        if isinstance(model_id, str):
            contains_ids.append(model_id)
    if sorted(contains_ids) != ["signaling", "social-proof"]:
        raise ProductDeltaGraphIncrementRehearsalError(
            "candidate review uniqueness coverage drifted"
        )


def _agent_proxy_schema(
    contract: Mapping[str, Any], phase: str
) -> dict[str, Any]:
    protocol = contract.get("agent_proxy_protocol")
    if isinstance(protocol, Mapping):
        phase_record = protocol.get(phase)
        if isinstance(phase_record, Mapping):
            schema = phase_record.get("response_schema")
            if isinstance(schema, Mapping):
                return copy.deepcopy(dict(schema))
    schemas = contract.get("agent_proxy_schemas")
    if isinstance(schemas, Mapping) and isinstance(schemas.get(phase), Mapping):
        return copy.deepcopy(dict(schemas[phase]))
    legacy_key = f"{phase}_agent_proxy_schema"
    schema = contract.get(legacy_key)
    if isinstance(schema, Mapping):
        return copy.deepcopy(dict(schema))
    raise ProductDeltaGraphIncrementRehearsalError(
        f"contract is missing agent proxy schema:{phase}"
    )


def _validate_declared_input_locks(
    *,
    contract: Mapping[str, Any],
    refs: Mapping[str, Mapping[str, Any]],
) -> None:
    locks = contract.get("input_locks")
    if locks is None:
        return
    if not isinstance(locks, Mapping):
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract input locks are malformed"
        )
    if set(locks) != set(refs):
        raise ProductDeltaGraphIncrementRehearsalError(
            "contract input locks do not cover the exact rehearsal inputs"
        )
    for name, declared in locks.items():
        if not isinstance(declared, Mapping):
            raise ProductDeltaGraphIncrementRehearsalError(
                f"contract input lock is malformed:{name}"
            )
        actual = refs[name]
        if declared.get("path") != actual.get("path"):
            raise ProductDeltaGraphIncrementRehearsalError(
                f"contract input path drift:{name}"
            )
        if declared.get("sha256") != actual.get("sha256"):
            raise ProductDeltaGraphIncrementRehearsalError(
                f"contract input hash drift:{name}"
            )


def _read_json_ref(
    root: Path, relpath: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    path = _resolve_repo_path(root, relpath)
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        raise ProductDeltaGraphIncrementRehearsalError(
            f"checked-in input could not be read:{relpath}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ProductDeltaGraphIncrementRehearsalError(
            f"checked-in JSON is invalid:{relpath}"
        ) from exc
    if not isinstance(value, dict):
        raise ProductDeltaGraphIncrementRehearsalError(
            f"checked-in JSON is not an object:{relpath}"
        )
    return value, _ref(relpath, raw)


def _read_text_ref(
    root: Path, relpath: str
) -> tuple[str, dict[str, Any]]:
    path = _resolve_repo_path(root, relpath)
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ProductDeltaGraphIncrementRehearsalError(
            f"checked-in text could not be read:{relpath}"
        ) from exc
    return text, _ref(relpath, raw)


def _ref(relpath: str, raw: bytes) -> dict[str, Any]:
    return {
        "path": relpath,
        "sha256": _sha256_bytes(raw),
        "bytes": len(raw),
    }


def _resolve_repo_path(root: Path, relpath: str) -> Path:
    candidate_rel = Path(relpath)
    if candidate_rel.is_absolute():
        raise ProductDeltaGraphIncrementRehearsalError(
            "absolute repository path is forbidden"
        )
    candidate = (root / candidate_rel).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ProductDeltaGraphIncrementRehearsalError(
            "repository path escapes the project root"
        ) from exc
    return candidate


def _assert_safe_generated(payloads: Mapping[str, Any]) -> None:
    rendered = json.dumps(payloads, ensure_ascii=False, sort_keys=True)
    for marker in SECRET_MARKERS:
        if marker in rendered:
            raise ProductDeltaGraphIncrementRehearsalError(
                "generated artifact contains a forbidden local-path or secret marker"
            )


def _required_mapping(
    value: Mapping[str, Any], key: str
) -> Mapping[str, Any]:
    child = value.get(key)
    if not isinstance(child, Mapping):
        raise ProductDeltaGraphIncrementRehearsalError(
            f"required object is missing:{key}"
        )
    return child


def _required_sequence(
    value: Mapping[str, Any], key: str
) -> Sequence[Any]:
    child = value.get(key)
    if not isinstance(child, list):
        raise ProductDeltaGraphIncrementRehearsalError(
            f"required array is missing:{key}"
        )
    return child


def _required_text(value: Mapping[str, Any], key: str) -> str:
    child = value.get(key)
    if not isinstance(child, str) or not child:
        raise ProductDeltaGraphIncrementRehearsalError(
            f"required text is missing:{key}"
        )
    return child


def _as_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ProductDeltaGraphIncrementRehearsalError(
            f"{label} is not an object"
        )
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _sha256_json_value(value: Any) -> str:
    return _sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
