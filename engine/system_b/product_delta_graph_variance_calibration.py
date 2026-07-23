"""Freeze exact rerun packets for bounded graph-variance calibration.

This prospective Product Delta helper reuses the completed direct-versus-current
one-hop rehearsal byte for byte. It creates two additional isolated samples per
condition behind neutral sample aliases and seals their lineage separately. It
does not generate an answer, call a provider, rerun the graph or planner, change
the skill, or judge graph value.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_graph_increment_rehearsal import (
    REHEARSAL_DIRECT,
    REHEARSAL_DIRECT_PLUS_ONE_HOP,
    validate_checked_in_rehearsal,
)
from engine.system_b.product_delta_graph_increment_rehearsal_result import (
    validate_checked_in_review_consolidation,
)


CONTRACT_SCHEMA_VERSION = (
    "lolla.product_delta_agent_graph_variance_calibration_contract.v1"
)
GENERATION_PACKETS_SCHEMA_VERSION = (
    "lolla.product_delta_agent_graph_variance_generation_packets.v1"
)
SEALED_MANIFEST_SCHEMA_VERSION = (
    "lolla.product_delta_agent_graph_variance_sealed_manifest.v1"
)
CALIBRATION_ID = "agent-only-graph-variance-calibration-2026-07-23"
BLINDING_NAMESPACE = "lolla-product-delta-graph-variance-calibration-v1"

DEFAULT_CONTRACT_RELPATH = (
    "docs/evals/lolla-agent-only-graph-variance-calibration-contract-v1.json"
)
PREDECESSOR_DIR_RELPATH = (
    "research/agent-only-graph-increment-rehearsal-2026-07-23"
)
PREDECESSOR_GENERATION_PACKETS_RELPATH = (
    f"{PREDECESSOR_DIR_RELPATH}/generation-packets.json"
)
PREDECESSOR_SEALED_MANIFEST_RELPATH = (
    f"{PREDECESSOR_DIR_RELPATH}/sealed-manifest.json"
)
PREDECESSOR_CONSOLIDATION_RELPATH = (
    f"{PREDECESSOR_DIR_RELPATH}/consolidated-diagnostic.json"
)
SOURCE_RELPATH = (
    "research/independent-phase5-cases-2026-07-12/useful-pressure-case.txt"
)
OUTPUT_DIR_RELPATH = (
    "research/agent-only-graph-variance-calibration-2026-07-23"
)
DEFAULT_GENERATION_PACKETS_RELPATH = f"{OUTPUT_DIR_RELPATH}/generation-packets.json"
DEFAULT_SEALED_MANIFEST_RELPATH = f"{OUTPUT_DIR_RELPATH}/sealed-manifest.json"

SAMPLE_ALIASES = (
    "sample-cinder",
    "sample-linen",
    "sample-moss",
    "sample-slate",
)
CONDITIONS = (
    REHEARSAL_DIRECT,
    REHEARSAL_DIRECT_PLUS_ONE_HOP,
)
REPLICATE_NUMBERS = (1, 2)

BOUNDARY = {
    "repository_provider_api_calls": 0,
    "repository_provider_api_cost_usd": 0.0,
    "repository_provider_execution_authorized": False,
    "codex_generation_contexts_predeclared": 4,
    "codex_blind_review_contexts_predeclared": 2,
    "codex_contexts_called_no_ai_calls_or_economically_free": False,
    "codex_platform_route_token_and_cost": "unavailable_to_repository_operator",
    "human_review_completed": False,
    "private_archives_read": False,
    "runtime_invoked": False,
    "live_skill_invoked": False,
    "graph_traversal_invoked": False,
    "graph_policy_changed": False,
    "planner_changed": False,
    "compiler_changed": False,
    "answer_quality_scored": False,
    "graph_causation_established": False,
    "human_usefulness_established": False,
}

NON_CLAIMS = (
    "not principal-human review",
    "not provider execution or an exact standalone provider envelope",
    "not a provider or model comparison",
    "not a statistically powered variance estimate",
    "not graph causation relevance value or usefulness evidence",
    "not proof that either answer is better",
    "not expected model behavior",
    "not completion of F2 or F3",
    "not permission to expand traversal",
    "not a live skill runtime planner compiler graph or interface change",
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


class ProductDeltaGraphVarianceCalibrationError(ValueError):
    """Sanitized deterministic contract or custody failure."""


def build_graph_variance_calibration(
    *, repo_root: Path | str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build four exact rerun packets and a separately sealed lineage map."""

    root = Path(repo_root).resolve()
    _validate_frozen_predecessor(root)

    contract, contract_ref = _read_json_ref(root, DEFAULT_CONTRACT_RELPATH)
    if contract.get("schema_version") != CONTRACT_SCHEMA_VERSION:
        raise ProductDeltaGraphVarianceCalibrationError(
            "graph-variance calibration contract schema mismatch"
        )
    _validate_contract(contract)

    locked_refs: dict[str, dict[str, Any]] = {}
    locked_payloads: dict[str, Any] = {}
    for name, declared in _required_mapping(contract, "input_locks").items():
        if not isinstance(declared, Mapping):
            raise ProductDeltaGraphVarianceCalibrationError(
                "input lock is not an object"
            )
        relpath = _required_text(declared, "path")
        raw, ref = _read_raw_ref(root, relpath)
        if ref != dict(declared):
            raise ProductDeltaGraphVarianceCalibrationError(
                f"locked predecessor drift:{name}"
            )
        locked_refs[str(name)] = ref
        if relpath.endswith(".json"):
            try:
                locked_payloads[str(name)] = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ProductDeltaGraphVarianceCalibrationError(
                    f"locked predecessor JSON invalid:{name}"
                ) from exc

    predecessor_generation = _required_mapping(
        locked_payloads, "predecessor_generation_packets"
    )
    predecessor_sealed = _required_mapping(
        locked_payloads, "predecessor_sealed_manifest"
    )
    predecessor_consolidation = _required_mapping(
        locked_payloads, "completed_predecessor_consolidation"
    )
    _validate_predecessor_semantics(
        generation=predecessor_generation,
        sealed=predecessor_sealed,
        consolidation=predecessor_consolidation,
    )

    packet_by_condition = _packet_by_condition(
        generation=predecessor_generation,
        sealed=predecessor_sealed,
    )
    assignments = _neutral_assignments()
    packets: list[dict[str, Any]] = []
    sealed_samples: dict[str, dict[str, Any]] = {}
    for sample_alias, condition, replicate_number in assignments:
        source_packet = packet_by_condition[condition]
        request = _required_mapping(source_packet, "request_body_projection")
        wrapper = _required_mapping(source_packet, "codex_task_wrapper")
        execution = _required_mapping(source_packet, "execution")
        packets.append(
            {
                "sample_alias": sample_alias,
                "request_body_projection": copy.deepcopy(dict(request)),
                "inheritance": {
                    "messages_inherited_byte_for_byte_as_json_values": True,
                    "response_schema_inherited_byte_for_byte_as_json_value": True,
                    "generation_settings_inherited_without_repair": True,
                    "request_body_projection_sha256": _sha256_json_value(request),
                    "task_wrapper_object_sha256": _sha256_json_value(wrapper),
                    "task_wrapper_text_sha256": _required_text(
                        wrapper, "sha256"
                    ),
                    "predecessor_packet_is_payload_source_not_new_execution": True,
                },
                "codex_task_wrapper": copy.deepcopy(dict(wrapper)),
                "execution": {
                    **copy.deepcopy(dict(execution)),
                    "performed": False,
                    "retry_or_fallback_authorized": False,
                    "sample_alias_is_not_condition_lineage": True,
                },
            }
        )
        sealed_samples[sample_alias] = {
            "condition": condition,
            "replicate_number": replicate_number,
            "predecessor_condition_alias": source_packet["condition_alias"],
            "request_body_projection_sha256": _sha256_json_value(request),
            "messages_sha256": _sha256_json_value(
                _required_sequence(request, "messages")
            ),
            "response_schema_sha256": _sha256_json_value(
                _required_mapping(request, "response_schema")
            ),
            "predeclared_terminal_output_path": (
                f"{OUTPUT_DIR_RELPATH}/terminal-output-{sample_alias}.json"
            ),
        }

    generation_payload = {
        "schema_version": GENERATION_PACKETS_SCHEMA_VERSION,
        "calibration_id": CALIBRATION_ID,
        "status": "frozen_neutral_replicate_packets_not_executed",
        "sample_count": 4,
        "sample_aliases": list(SAMPLE_ALIASES),
        "packets": packets,
        "blinding": {
            "sample_lineage_absent_from_packet_metadata": True,
            "semantic_packet_content_remains_exact_and_unredacted": True,
            "lineage_available_only_in_sealed_manifest": True,
        },
        "boundary": copy.deepcopy(BOUNDARY),
        "non_claims": list(NON_CLAIMS),
    }

    historical_outputs = _historical_output_map(
        locked_refs=locked_refs,
        sealed=predecessor_sealed,
    )
    sealed_payload = {
        "schema_version": SEALED_MANIFEST_SCHEMA_VERSION,
        "calibration_id": CALIBRATION_ID,
        "status": "sealed_before_new_agent_outputs",
        "contract_ref": contract_ref,
        "locked_predecessor_refs": locked_refs,
        "sample_map": sealed_samples,
        "historical_draw_zero": historical_outputs,
        "comparison_plan": _comparison_plan(sealed_samples, historical_outputs),
        "execution_budget": {
            "new_generation_contexts": 4,
            "new_blind_review_contexts": 2,
            "total_new_codex_contexts": 6,
            "repository_provider_api_calls": 0,
            "repository_provider_api_cost_usd": 0.0,
            "retry_fallback_healing_or_replacement_contexts": 0,
            "platform_route_token_and_cost": "unavailable_to_repository_operator",
        },
        "unblinding": {
            "generation_agents_receive_only_one_sample_packet": True,
            "blind_reviewers_receive_no_sample_map_or_pair_roles": True,
            "reveal_only_after_both_blind_reviews_are_frozen": True,
        },
        "boundary": copy.deepcopy(BOUNDARY),
        "non_claims": list(NON_CLAIMS),
    }
    _validate_built_payloads(
        generation=generation_payload,
        sealed=sealed_payload,
        packet_by_condition=packet_by_condition,
    )
    _assert_safe_generated(
        {"generation": generation_payload, "sealed": sealed_payload}
    )
    return generation_payload, sealed_payload


def render_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_checked_in_calibration(*, repo_root: Path | str) -> None:
    root = Path(repo_root).resolve()
    payloads = build_graph_variance_calibration(repo_root=root)
    for relpath, payload in zip(_output_relpaths(), payloads, strict=True):
        path = _resolve_repo_path(root, relpath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_json(payload), encoding="utf-8")


def validate_checked_in_calibration(*, repo_root: Path | str) -> list[str]:
    root = Path(repo_root).resolve()
    payloads = build_graph_variance_calibration(repo_root=root)
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


def _output_relpaths() -> tuple[str, str]:
    return DEFAULT_GENERATION_PACKETS_RELPATH, DEFAULT_SEALED_MANIFEST_RELPATH


def _validate_frozen_predecessor(root: Path) -> None:
    try:
        preoutput_errors = validate_checked_in_rehearsal(repo_root=root)
        result_errors = validate_checked_in_review_consolidation(repo_root=root)
    except (ValueError, KeyError, TypeError) as exc:
        raise ProductDeltaGraphVarianceCalibrationError(
            "completed predecessor validation failed"
        ) from exc
    if preoutput_errors or result_errors:
        raise ProductDeltaGraphVarianceCalibrationError(
            "completed predecessor artifact drifted"
        )


def _validate_contract(contract: Mapping[str, Any]) -> None:
    authorization = _required_mapping(contract, "authorization")
    expected_false = (
        "provider_backed_execution",
        "human_review",
        "private_archive_inspection",
        "human_usefulness_claim",
        "graph_policy_change",
        "traversal_expansion",
        "runtime_change",
        "live_skill_invocation",
        "answer_quality_scoring",
    )
    if any(authorization.get(key) is not False for key in expected_false):
        raise ProductDeltaGraphVarianceCalibrationError(
            "contract authorizes an out-of-scope action"
        )
    if authorization.get("provider_api_calls") != 0:
        raise ProductDeltaGraphVarianceCalibrationError(
            "contract provider-call boundary drifted"
        )
    generation = _required_mapping(contract, "generation_rehearsal")
    if generation.get("fresh_context_count") != 4:
        raise ProductDeltaGraphVarianceCalibrationError(
            "generation context count drifted"
        )
    if generation.get("retry_fallback_healing_or_replacement") is not False:
        raise ProductDeltaGraphVarianceCalibrationError(
            "contract permits retry or healing"
        )
    review = _required_mapping(contract, "blind_review_contract")
    if review.get("fresh_context_count") != 2 or review.get("pair_count") != 5:
        raise ProductDeltaGraphVarianceCalibrationError(
            "blind-review budget drifted"
        )
    comparison = _required_mapping(contract, "comparison_contract")
    if comparison.get("total_draws_per_condition_after_completion") != 3:
        raise ProductDeltaGraphVarianceCalibrationError(
            "replication count drifted"
        )
    if comparison.get("statistical_inference_authorized") is not False:
        raise ProductDeltaGraphVarianceCalibrationError(
            "statistical inference must remain unauthorized"
        )


def _validate_predecessor_semantics(
    *,
    generation: Mapping[str, Any],
    sealed: Mapping[str, Any],
    consolidation: Mapping[str, Any],
) -> None:
    if generation.get("packet_count") != 2:
        raise ProductDeltaGraphVarianceCalibrationError(
            "predecessor generation packet count drifted"
        )
    alias_map = _required_mapping(sealed, "alias_map")
    conditions = sorted(
        str(_required_mapping(alias_map, alias).get("condition"))
        for alias in alias_map
    )
    if conditions != sorted(CONDITIONS):
        raise ProductDeltaGraphVarianceCalibrationError(
            "predecessor condition lineage drifted"
        )
    if consolidation.get("status") != "valid_frozen_agent_diagnostic":
        raise ProductDeltaGraphVarianceCalibrationError(
            "predecessor result is not a valid frozen diagnostic"
        )
    boundary = _required_mapping(consolidation, "boundary")
    if boundary.get("graph_causation_established") is not False:
        raise ProductDeltaGraphVarianceCalibrationError(
            "predecessor causal boundary drifted"
        )


def _packet_by_condition(
    *, generation: Mapping[str, Any], sealed: Mapping[str, Any]
) -> dict[str, Mapping[str, Any]]:
    alias_map = _required_mapping(sealed, "alias_map")
    packets = {
        _required_text(item, "condition_alias"): item
        for item in _required_sequence(generation, "packets")
        if isinstance(item, Mapping)
    }
    by_condition: dict[str, Mapping[str, Any]] = {}
    for alias, lineage_value in alias_map.items():
        lineage = _as_mapping(lineage_value, "predecessor alias lineage")
        condition = _required_text(lineage, "condition")
        packet = _required_mapping(packets, str(alias))
        by_condition[condition] = packet
    if set(by_condition) != set(CONDITIONS):
        raise ProductDeltaGraphVarianceCalibrationError(
            "could not resolve both predecessor conditions"
        )
    return by_condition


def _neutral_assignments() -> list[tuple[str, str, int]]:
    assignments = [
        (condition, replicate_number)
        for condition in CONDITIONS
        for replicate_number in REPLICATE_NUMBERS
    ]
    assignments.sort(
        key=lambda item: _sha256_text(
            f"{BLINDING_NAMESPACE}|{item[0]}|{item[1]}"
        )
    )
    return [
        (sample_alias, condition, replicate_number)
        for sample_alias, (condition, replicate_number) in zip(
            SAMPLE_ALIASES, assignments, strict=True
        )
    ]


def _historical_output_map(
    *,
    locked_refs: Mapping[str, Mapping[str, Any]],
    sealed: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    alias_map = _required_mapping(sealed, "alias_map")
    output_lock_by_alias = {
        "condition-A": locked_refs["historical_terminal_output_condition_A"],
        "condition-B": locked_refs["historical_terminal_output_condition_B"],
    }
    result: dict[str, dict[str, Any]] = {}
    for alias, lineage_value in alias_map.items():
        lineage = _as_mapping(lineage_value, "historical alias lineage")
        condition = _required_text(lineage, "condition")
        result[condition] = {
            "draw_number": 0,
            "predecessor_condition_alias": alias,
            "terminal_output_ref": copy.deepcopy(
                dict(output_lock_by_alias[str(alias)])
            ),
        }
    if set(result) != set(CONDITIONS):
        raise ProductDeltaGraphVarianceCalibrationError(
            "historical draw-zero lineage drifted"
        )
    return result


def _comparison_plan(
    sealed_samples: Mapping[str, Mapping[str, Any]],
    historical_outputs: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    samples_by_condition_and_draw = {
        (str(item["condition"]), int(item["replicate_number"])): alias
        for alias, item in sealed_samples.items()
    }
    direct = REHEARSAL_DIRECT
    graph = REHEARSAL_DIRECT_PLUS_ONE_HOP
    refs = {
        (direct, 0): _required_mapping(
            _required_mapping(historical_outputs, direct),
            "terminal_output_ref",
        )["path"],
        (graph, 0): _required_mapping(
            _required_mapping(historical_outputs, graph),
            "terminal_output_ref",
        )["path"],
    }
    for key, alias in samples_by_condition_and_draw.items():
        refs[key] = f"{OUTPUT_DIR_RELPATH}/terminal-output-{alias}.json"
    declared = (
        ("within-direct-fresh", "within_condition", (direct, 1), (direct, 2)),
        ("within-graph-fresh", "within_condition", (graph, 1), (graph, 2)),
        ("cross-historical", "cross_condition", (direct, 0), (graph, 0)),
        ("cross-fresh-1", "cross_condition", (direct, 1), (graph, 1)),
        ("cross-fresh-2", "cross_condition", (direct, 2), (graph, 2)),
    )
    plan: list[dict[str, Any]] = []
    for pair_id, pair_role, left, right in declared:
        plan.append(
            {
                "pair_id": pair_id,
                "sealed_pair_role": pair_role,
                "left": {
                    "condition": left[0],
                    "draw_number": left[1],
                    "terminal_output_path": refs[left],
                },
                "right": {
                    "condition": right[0],
                    "draw_number": right[1],
                    "terminal_output_path": refs[right],
                },
                "blind_arm_orientation": "derived_deterministically_after_outputs_exist",
            }
        )
    return plan


def _validate_built_payloads(
    *,
    generation: Mapping[str, Any],
    sealed: Mapping[str, Any],
    packet_by_condition: Mapping[str, Mapping[str, Any]],
) -> None:
    packets = _required_sequence(generation, "packets")
    if len(packets) != 4:
        raise ProductDeltaGraphVarianceCalibrationError(
            "built sample count drifted"
        )
    sample_map = _required_mapping(sealed, "sample_map")
    counts = {condition: 0 for condition in CONDITIONS}
    for item in packets:
        packet = _as_mapping(item, "generated sample packet")
        alias = _required_text(packet, "sample_alias")
        lineage = _required_mapping(sample_map, alias)
        condition = _required_text(lineage, "condition")
        counts[condition] += 1
        source = _required_mapping(packet_by_condition, condition)
        if packet["request_body_projection"] != source["request_body_projection"]:
            raise ProductDeltaGraphVarianceCalibrationError(
                "sample request differs from frozen predecessor"
            )
        if packet["codex_task_wrapper"] != source["codex_task_wrapper"]:
            raise ProductDeltaGraphVarianceCalibrationError(
                "sample wrapper differs from frozen predecessor"
            )
    if set(_required_sequence(generation, "sample_aliases")) != set(SAMPLE_ALIASES):
        raise ProductDeltaGraphVarianceCalibrationError(
            "sample aliases drifted"
        )
    if counts != {condition: 2 for condition in CONDITIONS}:
        raise ProductDeltaGraphVarianceCalibrationError(
            "sample allocation is not two per condition"
        )
    plan = _required_sequence(sealed, "comparison_plan")
    if len(plan) != 5:
        raise ProductDeltaGraphVarianceCalibrationError(
            "comparison plan count drifted"
        )
    roles = [str(_as_mapping(item, "comparison").get("sealed_pair_role")) for item in plan]
    if roles.count("within_condition") != 2 or roles.count("cross_condition") != 3:
        raise ProductDeltaGraphVarianceCalibrationError(
            "comparison role allocation drifted"
        )


def _read_json_ref(
    root: Path, relpath: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    raw, ref = _read_raw_ref(root, relpath)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProductDeltaGraphVarianceCalibrationError(
            f"invalid JSON input:{relpath}"
        ) from exc
    if not isinstance(payload, dict):
        raise ProductDeltaGraphVarianceCalibrationError(
            f"JSON input is not an object:{relpath}"
        )
    return payload, ref


def _read_raw_ref(
    root: Path, relpath: str
) -> tuple[bytes, dict[str, Any]]:
    path = _resolve_repo_path(root, relpath)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ProductDeltaGraphVarianceCalibrationError(
            f"missing input:{relpath}"
        ) from exc
    return raw, {
        "path": relpath,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def _resolve_repo_path(root: Path, relpath: str) -> Path:
    if not relpath or Path(relpath).is_absolute():
        raise ProductDeltaGraphVarianceCalibrationError(
            "repository-relative path required"
        )
    resolved = (root / relpath).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ProductDeltaGraphVarianceCalibrationError(
            "path escapes repository root"
        ) from exc
    return resolved


def _required_mapping(
    value: Mapping[str, Any], key: str
) -> Mapping[str, Any]:
    item = value.get(key)
    if not isinstance(item, Mapping):
        raise ProductDeltaGraphVarianceCalibrationError(
            f"required object missing:{key}"
        )
    return item


def _required_sequence(
    value: Mapping[str, Any], key: str
) -> Sequence[Any]:
    item = value.get(key)
    if not isinstance(item, list):
        raise ProductDeltaGraphVarianceCalibrationError(
            f"required list missing:{key}"
        )
    return item


def _required_text(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise ProductDeltaGraphVarianceCalibrationError(
            f"required text missing:{key}"
        )
    return item


def _as_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ProductDeltaGraphVarianceCalibrationError(
            f"{label} is not an object"
        )
    return value


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_json_value(value: Any) -> str:
    canonical = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return _sha256_text(canonical)


def _assert_safe_generated(payloads: Mapping[str, Any]) -> None:
    rendered = render_json(payloads)
    for marker in SECRET_MARKERS:
        if marker in rendered:
            raise ProductDeltaGraphVarianceCalibrationError(
                "generated artifact contains forbidden secret or local-path marker"
            )
