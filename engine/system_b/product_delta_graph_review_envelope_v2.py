"""Build the prospective structured-output repair for graph replication review.

This module deepens the existing offline Product Delta owner. It reuses the
consumed graph-replication source, answers, controls, comparison orientation,
and deterministic validators while replacing the ambiguous reviewer-facing
response example with an authoritative JSON Schema.

The module is provider-free. It does not invoke Codex, call a provider, alter
the graph, reinterpret an answer, repair the failed historical review, reveal
sealed lineage, or authorize a semantic rerun.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_graph_replication_result import (
    COMPARISON_CASE_IDS,
    NON_CLAIMS,
    REVIEW_SCHEMA_VERSION as REVIEW_SCHEMA_VERSION_V1,
    _review_boundary,
    _validate_review,
)
from engine.system_b.product_delta_paired_screen_review import (
    COGNITIVE_EFFECT_VALUES,
    MATERIAL_DIFFERENCE_VALUES,
    PRESENCE_VALUES,
    QUALIFICATION_DISPOSITIONS,
    REASONING_OPERATION_VALUES,
    SOURCE_GROUNDING_VALUES,
    STANDDOWN_SUPPORT_VALUES,
)


REPAIR_ID = "lolla-agent-only-graph-review-envelope-repair-v1"
DATE = "2026-07-24"
REVIEW_PACKET_SCHEMA_VERSION = (
    "lolla.product_delta_graph_replication_blind_review_packet.v2"
)
REVIEW_SCHEMA_VERSION = (
    "lolla.product_delta_graph_replication_fresh_agent_review.v2"
)
POST_REVEAL_SCHEMA_VERSION = (
    "lolla.product_delta_graph_replication_post_reveal_interpretation.v2"
)

SOURCE_REPLICATION_DIR = "research/agent-only-graph-replication-2026-07-23"
SOURCE_REVIEW_DIR = "reviews/codex-assisted/agent-only-graph-replication-v1"
OUTPUT_DIR = "research/agent-only-graph-review-envelope-repair-2026-07-24"
FUTURE_REVIEW_DIR = (
    "reviews/codex-assisted/agent-only-graph-review-envelope-v2"
)

CONTRACT_RELPATH = (
    "docs/evals/lolla-agent-only-graph-review-envelope-repair-contract-v1.json"
)
BLIND_PACKET_RELPATH = (
    f"{SOURCE_REPLICATION_DIR}/blind-review-packet.json"
)
EXECUTION_MANIFEST_RELPATH = (
    f"{SOURCE_REPLICATION_DIR}/execution-sealed-manifest.json"
)
SOURCE_CONTRACT_RELPATH = (
    "docs/evals/lolla-agent-only-graph-replication-contract-v1.json"
)
SOURCE_CONSOLIDATION_RELPATH = (
    f"{SOURCE_REPLICATION_DIR}/consolidated-diagnostic.json"
)
SOURCE_PRIMARY_REVIEW_RELPATH = (
    f"{SOURCE_REVIEW_DIR}/pair-review-primary.json"
)
SOURCE_SKEPTICAL_REVIEW_RELPATH = (
    f"{SOURCE_REVIEW_DIR}/pair-review-skeptical.json"
)
SOURCE_SKEPTICAL_FAILURE_RELPATH = (
    f"{SOURCE_REVIEW_DIR}/pair-review-skeptical-terminal-failure.json"
)

LANES = ("primary", "skeptical")
REVIEW_IDS = {
    "primary": "agent-graph-review-envelope-v2-primary",
    "skeptical": "agent-graph-review-envelope-v2-skeptical",
}
INTERPRETATION_IDS = {
    "primary": "agent-graph-review-envelope-v2-pattern-primary",
    "skeptical": "agent-graph-review-envelope-v2-pattern-skeptical",
}
SCHEMA_RELPATHS = {
    lane: f"{OUTPUT_DIR}/schemas/blind-review-{lane}.schema.json"
    for lane in LANES
}
POST_REVEAL_SCHEMA_RELPATHS = {
    lane: f"{OUTPUT_DIR}/schemas/post-reveal-{lane}.schema.json"
    for lane in LANES
}
PACKET_RELPATHS = {
    lane: f"{OUTPUT_DIR}/blind-review-packet-{lane}.json"
    for lane in LANES
}
FUTURE_REVIEW_RELPATHS = {
    lane: f"{FUTURE_REVIEW_DIR}/pair-review-{lane}.json"
    for lane in LANES
}
FUTURE_REVIEW_FAILURE_RELPATHS = {
    lane: (
        f"{FUTURE_REVIEW_DIR}/pair-review-{lane}-terminal-failure.json"
    )
    for lane in LANES
}
FUTURE_POST_REVEAL_PACKET_RELPATHS = {
    lane: f"{OUTPUT_DIR}/post-reveal-packet-{lane}.json"
    for lane in LANES
}
FUTURE_INTERPRETATION_RELPATHS = {
    lane: f"{FUTURE_REVIEW_DIR}/pattern-interpretation-{lane}.json"
    for lane in LANES
}
VALID_FIXTURE_RELPATH = (
    f"{OUTPUT_DIR}/fixtures/blind-review-valid-scalar.json"
)
INVALID_FIXTURE_RELPATH = (
    f"{OUTPUT_DIR}/fixtures/blind-review-invalid-array.json"
)
POST_REVEAL_FIXTURE_RELPATHS = {
    lane: f"{OUTPUT_DIR}/fixtures/post-reveal-valid-{lane}.json"
    for lane in LANES
}
FIXTURE_RECEIPT_RELPATH = f"{OUTPUT_DIR}/fixture-validation-receipt.json"
FUTURE_CONSOLIDATION_RELPATH = f"{OUTPUT_DIR}/consolidated-diagnostic.json"
FUTURE_RESULT_RELPATH = (
    "docs/conversation-understanding/"
    "lolla-agent-only-graph-review-envelope-v2-result-2026-07-24.md"
)

FROZEN_INPUT_LOCKS = {
    SOURCE_CONTRACT_RELPATH: {
        "bytes": 17466,
        "sha256": (
            "2b772fe4da84510c7bb9083c62038febe82c8f95d91ce3a07ff8153cb9fd2068"
        ),
    },
    BLIND_PACKET_RELPATH: {
        "bytes": 98006,
        "sha256": (
            "26d298f8c2f4d44ae9fce8704303e23d536d5d75c359d86a62d86b7db7a268ab"
        ),
    },
    EXECUTION_MANIFEST_RELPATH: {
        "bytes": 26537,
        "sha256": (
            "cfec80403cffec63e77416f5cf0695eb492ab8df970f0937a1e72fe2c777eb8a"
        ),
    },
    SOURCE_PRIMARY_REVIEW_RELPATH: {
        "bytes": 38372,
        "sha256": (
            "8fdd3eb60d03b3c07c9fe092fd3940acf4b4f53d019bcd64be991c1b96238ec6"
        ),
    },
    SOURCE_SKEPTICAL_REVIEW_RELPATH: {
        "bytes": 42279,
        "sha256": (
            "60f19ac3c2364db98709399d321f87fbae8967051b516143952b752c39b1fe84"
        ),
    },
    SOURCE_SKEPTICAL_FAILURE_RELPATH: {
        "bytes": 3462,
        "sha256": (
            "1ccd8a0caffa6a6bcddc480f0bf24a6b21409273efcaf97c93f72a37c667fe36"
        ),
    },
    SOURCE_CONSOLIDATION_RELPATH: {
        "bytes": 62536,
        "sha256": (
            "6c2a5a603e6ade498466155f92590d8ba333be4d43e34f8d5ba5ddab97bc615a"
        ),
    },
}

REVIEW_SPECIFIC_PATTERN_STATES = (
    "cross_condition_difference_more_consistent_than_"
    "observed_within_condition_variation",
    "cross_condition_difference_not_distinguishable_from_"
    "observed_within_condition_variation",
    "review_specific_pattern_mixed_or_uncertain",
)

EXACT_AUTHORIZATION = (
    "AUTHORIZE_LOLLA_GRAPH_REVIEW_ENVELOPE_V2: "
    "reuse_frozen_generation_outputs=true; blind_review_contexts=2; "
    "conditional_post_reveal_contexts=2; maximum_codex_contexts=4; "
    "repository_provider_api_calls=0; "
    "repository_provider_api_cost_usd=0.00; no_retry=true"
)


class ProductDeltaGraphReviewEnvelopeV2Error(ValueError):
    """Sanitized deterministic envelope-repair failure."""


def render_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload, ensure_ascii=False, indent=2, sort_keys=True
    ) + "\n"


def build_artifacts(*, repo_root: Path | str) -> dict[str, dict[str, Any]]:
    """Build every provider-free prospective artifact."""

    root = Path(repo_root).resolve()
    locked = _load_locked_inputs(root)
    blind = locked[BLIND_PACKET_RELPATH]
    primary = locked[SOURCE_PRIMARY_REVIEW_RELPATH]
    skeptical = locked[SOURCE_SKEPTICAL_REVIEW_RELPATH]

    if not isinstance(blind, Mapping):
        raise ProductDeltaGraphReviewEnvelopeV2Error(
            "frozen blind packet is not an object"
        )
    schemas = {
        lane: _build_review_schema(blind=blind, lane=lane)
        for lane in LANES
    }
    post_schemas = {
        lane: _build_post_reveal_schema(lane=lane)
        for lane in LANES
    }
    schema_refs = {
        lane: _ref_for_payload(SCHEMA_RELPATHS[lane], schemas[lane])
        for lane in LANES
    }
    post_schema_refs = {
        lane: _ref_for_payload(
            POST_REVEAL_SCHEMA_RELPATHS[lane], post_schemas[lane]
        )
        for lane in LANES
    }
    packets = {
        lane: _build_review_packet(
            blind=blind,
            lane=lane,
            schema_ref=schema_refs[lane],
        )
        for lane in LANES
    }

    valid_fixture = _adapt_historical_review_fixture(
        primary,
        review_id=REVIEW_IDS["primary"],
    )
    invalid_fixture = _adapt_historical_review_fixture(
        skeptical,
        review_id=REVIEW_IDS["skeptical"],
    )
    post_fixtures = {
        lane: _build_post_reveal_fixture(lane=lane)
        for lane in LANES
    }
    fixture_receipt = _build_fixture_receipt(
        valid_fixture=valid_fixture,
        invalid_fixture=invalid_fixture,
        review_schemas=schemas,
        post_fixtures=post_fixtures,
        post_schemas=post_schemas,
    )

    artifacts: dict[str, dict[str, Any]] = {}
    for lane in LANES:
        artifacts[SCHEMA_RELPATHS[lane]] = schemas[lane]
        artifacts[POST_REVEAL_SCHEMA_RELPATHS[lane]] = post_schemas[lane]
        artifacts[PACKET_RELPATHS[lane]] = packets[lane]
        artifacts[POST_REVEAL_FIXTURE_RELPATHS[lane]] = post_fixtures[lane]
    artifacts[VALID_FIXTURE_RELPATH] = valid_fixture
    artifacts[INVALID_FIXTURE_RELPATH] = invalid_fixture
    artifacts[FIXTURE_RECEIPT_RELPATH] = fixture_receipt

    generated_refs = {
        relpath: _ref_for_payload(relpath, payload)
        for relpath, payload in artifacts.items()
    }
    artifacts[CONTRACT_RELPATH] = _build_contract(
        generated_refs=generated_refs,
        schema_refs=schema_refs,
        post_schema_refs=post_schema_refs,
    )
    return artifacts


def write_artifacts(*, repo_root: Path | str) -> None:
    root = Path(repo_root).resolve()
    for relpath, payload in build_artifacts(repo_root=root).items():
        target = _resolve_repo_path(root, relpath)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_json(payload), encoding="utf-8")


def validate_checked_in_artifacts(
    *, repo_root: Path | str
) -> list[str]:
    root = Path(repo_root).resolve()
    errors: list[str] = []
    try:
        expected = build_artifacts(repo_root=root)
    except ProductDeltaGraphReviewEnvelopeV2Error as exc:
        return [str(exc)]
    for relpath, payload in expected.items():
        target = _resolve_repo_path(root, relpath)
        try:
            actual = target.read_text(encoding="utf-8")
        except OSError:
            errors.append(f"missing generated artifact:{relpath}")
            continue
        if actual != render_json(payload):
            errors.append(f"generated artifact drift:{relpath}")
    for relpath in (
        *FUTURE_REVIEW_RELPATHS.values(),
        *FUTURE_REVIEW_FAILURE_RELPATHS.values(),
        *FUTURE_POST_REVEAL_PACKET_RELPATHS.values(),
        *FUTURE_INTERPRETATION_RELPATHS.values(),
        FUTURE_CONSOLIDATION_RELPATH,
        FUTURE_RESULT_RELPATH,
    ):
        if _resolve_repo_path(root, relpath).exists():
            errors.append(f"unauthorized semantic result exists:{relpath}")
    return errors


def validate_v2_review(
    payload: Mapping[str, Any],
    *,
    blind: Mapping[str, Any],
    lane: str,
    schema: Mapping[str, Any],
) -> list[str]:
    """Apply structural schema checks and the existing semantic-shape owner."""

    if lane not in LANES:
        return ["unknown review lane"]
    errors = validate_json_schema_subset(payload, schema)
    adapted = copy.deepcopy(dict(payload))
    adapted["schema_version"] = REVIEW_SCHEMA_VERSION_V1
    adapted["review_id"] = (
        "agent-graph-replication-pair-primary-v1"
        if lane == "primary"
        else "agent-graph-replication-pair-skeptical-v1"
    )
    errors.extend(
        _validate_review(
            adapted,
            expected_review_id=adapted["review_id"],
            blind=blind,
        )
    )
    return errors


def validate_json_schema_subset(
    value: Any,
    schema: Mapping[str, Any],
    *,
    path: str = "$",
) -> list[str]:
    """Validate the conservative JSON-Schema subset used by this contract."""

    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type is not None and not _matches_json_type(
        value, str(expected_type)
    ):
        return [f"{path}:expected {expected_type}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}:value outside enum")

    if expected_type == "object" and isinstance(value, Mapping):
        properties = schema.get("properties", {})
        if not isinstance(properties, Mapping):
            return [f"{path}:schema properties malformed"]
        required = schema.get("required", [])
        if not isinstance(required, Sequence) or isinstance(
            required, (str, bytes)
        ):
            return [f"{path}:schema required malformed"]
        for key in required:
            if key not in value:
                errors.append(f"{path}:missing required property {key}")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}:unexpected property {key}")
        for key, child_schema in properties.items():
            if key in value and isinstance(child_schema, Mapping):
                errors.extend(
                    validate_json_schema_subset(
                        value[key],
                        child_schema,
                        path=f"{path}.{key}",
                    )
                )

    if expected_type == "array" and isinstance(value, list):
        minimum = schema.get("minItems")
        maximum = schema.get("maxItems")
        if isinstance(minimum, int) and len(value) < minimum:
            errors.append(f"{path}:fewer than {minimum} items")
        if isinstance(maximum, int) and len(value) > maximum:
            errors.append(f"{path}:more than {maximum} items")
        item_schema = schema.get("items")
        if isinstance(item_schema, Mapping):
            for index, item in enumerate(value):
                errors.extend(
                    validate_json_schema_subset(
                        item,
                        item_schema,
                        path=f"{path}[{index}]",
                    )
                )
    return errors


def _build_review_schema(
    *, blind: Mapping[str, Any], lane: str
) -> dict[str, Any]:
    qualification_ids = _case_ids(
        _required_list(blind, "qualification_cases")
    )
    comparison_ids = _case_ids(
        _required_list(blind, "comparison_cases")
    )
    standdown_ids = _case_ids(_required_list(blind, "standdown_cases"))
    duplicate_id = str(
        _required_mapping(blind, "exact_duplicate_null")["case_id"]
    )
    if comparison_ids != list(COMPARISON_CASE_IDS):
        raise ProductDeltaGraphReviewEnvelopeV2Error(
            "frozen comparison identities drifted"
        )
    available = _available_review_schema(
        case_ids=comparison_ids,
    )
    duplicate = _available_review_schema(case_ids=[duplicate_id])
    qualification = _closed_object(
        {
            "case_id": _enum_string(qualification_ids),
            "evidence_disposition": _enum_string(
                sorted(QUALIFICATION_DISPOSITIONS)
            ),
            "supported_observations": _string_array(),
            "missing_evidence": _string_array(),
            "inferences_explicitly_not_made": _string_array(),
            "uncertainty_notes": _string_array(),
        }
    )
    standdown = _closed_object(
        {
            "case_id": _enum_string(standdown_ids),
            "standdown_support": _enum_string(
                sorted(STANDDOWN_SUPPORT_VALUES)
            ),
            "source_basis": _string_array(),
            "risk_of_forced_additional_analysis": _string_array(),
            "semantic_limits_of_mechanical_observation": _string_array(),
        }
    )
    boundary = _closed_object(
        {
            "answer_quality_scored": _enum_boolean(False),
            "ground_truth": _enum_boolean(False),
            "human_validated": _enum_boolean(False),
            "provider_calls": {"type": "integer", "enum": [0]},
            "winner_selected": _enum_boolean(False),
        }
    )
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": f"Lolla graph replication blind review v2 ({lane})",
        "type": "object",
        "properties": {
            "schema_version": _enum_string([REVIEW_SCHEMA_VERSION]),
            "review_id": _enum_string([REVIEW_IDS[lane]]),
            "fresh_context": _enum_boolean(True),
            "saw_lineage_before_freeze": _enum_boolean(False),
            "saw_sibling_review_before_freeze": _enum_boolean(False),
            "boundary": boundary,
            "qualification_reviews": _fixed_array(
                qualification, len(qualification_ids)
            ),
            "duplicate_null_review": duplicate,
            "comparison_reviews": _fixed_array(
                available, len(comparison_ids)
            ),
            "standdown_reviews": _fixed_array(
                standdown, len(standdown_ids)
            ),
        },
        "required": [
            "schema_version",
            "review_id",
            "fresh_context",
            "saw_lineage_before_freeze",
            "saw_sibling_review_before_freeze",
            "boundary",
            "qualification_reviews",
            "duplicate_null_review",
            "comparison_reviews",
            "standdown_reviews",
        ],
        "additionalProperties": False,
    }


def _available_review_schema(*, case_ids: Sequence[str]) -> dict[str, Any]:
    atomic_move = _closed_object(
        {
            "move_id": {"type": "string"},
            "summary": {"type": "string"},
            "presence": _enum_string(sorted(PRESENCE_VALUES)),
            "reasoning_operation": _enum_string(
                sorted(REASONING_OPERATION_VALUES)
            ),
            "source_evidence": _string_array(),
            "source_grounding": _enum_string(
                sorted(SOURCE_GROUNDING_VALUES)
            ),
            "cognitive_effect": _enum_string(
                sorted(COGNITIVE_EFFECT_VALUES)
            ),
            "decision_effect": {"type": "string"},
        }
    )
    arm_observation = _closed_object(
        {
            "preserved_source_value": _string_array(),
            "lost_or_weakened_source_value": _string_array(),
            "unsupported_additions": _string_array(),
            "cognitive_burden": _string_array(),
        }
    )
    return _closed_object(
        {
            "case_id": _enum_string(list(case_ids)),
            "review_status": _enum_string(["reviewed"]),
            "source_interpretation": _closed_object(
                {
                    "decision_or_question": {"type": "string"},
                    "material_constraints": _string_array(),
                    "source_limits": _string_array(),
                }
            ),
            "atomic_moves": {
                "type": "array",
                "items": atomic_move,
                "minItems": 1,
                "maxItems": 4,
            },
            "arm_observations": _closed_object(
                {
                    "A": copy.deepcopy(arm_observation),
                    "B": copy.deepcopy(arm_observation),
                }
            ),
            "material_decision_difference": _enum_string(
                sorted(MATERIAL_DIFFERENCE_VALUES)
            ),
            "inspection_limits": _string_array(),
        }
    )


def _build_post_reveal_schema(*, lane: str) -> dict[str, Any]:
    assessment = _closed_object(
        {
            "case_id": _enum_string(list(COMPARISON_CASE_IDS)),
            "sealed_pair_role": _enum_string(
                ["within_condition", "cross_condition"]
            ),
            "frozen_material_decision_difference": _enum_string(
                sorted(MATERIAL_DIFFERENCE_VALUES)
            ),
            "cited_frozen_move_ids": _string_array(),
            "recurrence_observation": {"type": "string"},
            "burden_harm_or_lost_value_observation": {"type": "string"},
            "uncertainty": {"type": "string"},
        }
    )
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": f"Lolla graph replication post-reveal read v2 ({lane})",
        "type": "object",
        "properties": {
            "schema_version": _enum_string([POST_REVEAL_SCHEMA_VERSION]),
            "interpretation_id": _enum_string(
                [INTERPRETATION_IDS[lane]]
            ),
            "source_review_id": _enum_string([REVIEW_IDS[lane]]),
            "fresh_post_reveal_context": _enum_boolean(True),
            "saw_sibling_review_or_interpretation": _enum_boolean(False),
            "state": _enum_string(list(REVIEW_SPECIFIC_PATTERN_STATES)),
            "pair_assessments": _fixed_array(
                assessment, len(COMPARISON_CASE_IDS)
            ),
            "rationale": {"type": "string"},
            "nonclaims_acknowledged": _fixed_array(
                {"type": "string"}, len(NON_CLAIMS)
            ),
        },
        "required": [
            "schema_version",
            "interpretation_id",
            "source_review_id",
            "fresh_post_reveal_context",
            "saw_sibling_review_or_interpretation",
            "state",
            "pair_assessments",
            "rationale",
            "nonclaims_acknowledged",
        ],
        "additionalProperties": False,
    }


def _build_review_packet(
    *,
    blind: Mapping[str, Any],
    lane: str,
    schema_ref: Mapping[str, Any],
) -> dict[str, Any]:
    packet = {
        "schema_version": REVIEW_PACKET_SCHEMA_VERSION,
        "repair_id": REPAIR_ID,
        "lane": lane,
        "status": (
            "prospective_provider_free_packet_frozen_"
            "semantic_execution_not_authorized"
        ),
        "purpose": blind["purpose"],
        "evidence_class": (
            "provider_free_structured_output_envelope_repair_"
            "not_semantic_or_graph_evidence"
        ),
        "one_allowed_causal_change": (
            "Replace the ambiguous example-shaped reviewer response envelope "
            "with one authoritative JSON Schema supplied through Codex "
            "--output-schema. Source, answers, controls, comparison "
            "orientation, review grammar, and graph lineage remain frozen."
        ),
        "source_blind_packet": _locked_ref(BLIND_PACKET_RELPATH),
        "boundary": {
            "repository_provider_api_calls": 0,
            "repository_provider_api_cost_usd": 0.0,
            "semantic_execution_authorized": False,
            "new_codex_contexts_authorized": 0,
            "historical_review_repaired_or_reinterpreted": False,
            "graph_or_runtime_change": False,
            "answer_quality_scored": False,
            "winner_selected": False,
            "human_usefulness_established": False,
        },
        "authoritative_source": copy.deepcopy(
            blind["authoritative_source"]
        ),
        "review_order": copy.deepcopy(blind["review_order"]),
        "visibility": copy.deepcopy(blind["visibility"]),
        "review_contract": {
            "shape_owner": copy.deepcopy(dict(schema_ref)),
            "scalar_enum_rule": (
                "Every enum-valued field contains exactly one JSON string, "
                "never an array. Allowed-values arrays below describe the "
                "domain; they are not the response cardinality."
            ),
            "enum_fields": {
                "evidence_disposition": {
                    "json_type": "string",
                    "cardinality": "exactly_one",
                    "allowed_values": sorted(QUALIFICATION_DISPOSITIONS),
                },
                "presence": {
                    "json_type": "string",
                    "cardinality": "exactly_one",
                    "allowed_values": sorted(PRESENCE_VALUES),
                },
                "reasoning_operation": {
                    "json_type": "string",
                    "cardinality": "exactly_one",
                    "allowed_values": sorted(REASONING_OPERATION_VALUES),
                },
                "source_grounding": {
                    "json_type": "string",
                    "cardinality": "exactly_one",
                    "allowed_values": sorted(SOURCE_GROUNDING_VALUES),
                },
                "cognitive_effect": {
                    "json_type": "string",
                    "cardinality": "exactly_one",
                    "allowed_values": sorted(COGNITIVE_EFFECT_VALUES),
                },
                "material_decision_difference": {
                    "json_type": "string",
                    "cardinality": "exactly_one",
                    "allowed_values": sorted(MATERIAL_DIFFERENCE_VALUES),
                },
                "standdown_support": {
                    "json_type": "string",
                    "cardinality": "exactly_one",
                    "allowed_values": sorted(STANDDOWN_SUPPORT_VALUES),
                },
            },
            "atomic_move_count_per_available_comparison": {
                "minimum": 1,
                "maximum": 4,
            },
            "forbidden_review_behavior": copy.deepcopy(
                blind["review_contract"]["forbidden_review_behavior"]
            ),
        },
        "structured_output_contract": {
            "authoritative_schema": copy.deepcopy(dict(schema_ref)),
            "execution_flag": "--output-schema",
            "schema_enforced_at_generation_boundary": True,
            "deterministic_local_validation_after_capture": True,
            "schema_proves_shape_not_semantic_correctness": True,
            "first_terminal_payload_only": True,
            "retry_fallback_healing_replacement_or_reformatting": False,
        },
        "task_wrapper": _review_task_wrapper(lane=lane),
        "qualification_cases": copy.deepcopy(blind["qualification_cases"]),
        "exact_duplicate_null": copy.deepcopy(
            blind["exact_duplicate_null"]
        ),
        "comparison_case_count": blind["comparison_case_count"],
        "comparison_cases": copy.deepcopy(blind["comparison_cases"]),
        "standdown_cases": copy.deepcopy(blind["standdown_cases"]),
        "pre_review_mechanical_availability": copy.deepcopy(
            blind["pre_review_mechanical_availability"]
        ),
        "non_claims": copy.deepcopy(blind["non_claims"]),
    }
    _assert_semantic_inputs_preserved(packet=packet, blind=blind)
    _assert_no_ambiguous_shape(packet)
    return packet


def _build_fixture_receipt(
    *,
    valid_fixture: Mapping[str, Any],
    invalid_fixture: Mapping[str, Any],
    review_schemas: Mapping[str, Mapping[str, Any]],
    post_fixtures: Mapping[str, Mapping[str, Any]],
    post_schemas: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    valid_errors = validate_json_schema_subset(
        valid_fixture, review_schemas["primary"]
    )
    invalid_errors = validate_json_schema_subset(
        invalid_fixture, review_schemas["skeptical"]
    )
    cognitive_errors = [
        error
        for error in invalid_errors
        if ".cognitive_effect:expected string" in error
    ]
    post_errors = {
        lane: validate_json_schema_subset(
            post_fixtures[lane], post_schemas[lane]
        )
        for lane in LANES
    }
    if valid_errors:
        raise ProductDeltaGraphReviewEnvelopeV2Error(
            "known-valid scalar review fixture failed v2 schema"
        )
    if len(cognitive_errors) != 29 or len(invalid_errors) != 29:
        raise ProductDeltaGraphReviewEnvelopeV2Error(
            "historical 29-array failure was not reproduced exactly"
        )
    if any(post_errors.values()):
        raise ProductDeltaGraphReviewEnvelopeV2Error(
            "post-reveal structural fixture failed v2 schema"
        )
    return {
        "schema_version": (
            "lolla.product_delta_graph_review_envelope_fixture_receipt.v1"
        ),
        "repair_id": REPAIR_ID,
        "date": DATE,
        "status": "provider_free_shape_repair_fixture_gate_passed",
        "evidence_class": (
            "development_shape_fixture_not_semantic_graph_or_usefulness_evidence"
        ),
        "valid_scalar_fixture": {
            "path": VALID_FIXTURE_RELPATH,
            "schema_lane": "primary",
            "validation_error_count": 0,
            "meaning_validated": False,
        },
        "historical_invalid_array_fixture": {
            "path": INVALID_FIXTURE_RELPATH,
            "schema_lane": "skeptical",
            "validation_error_count": 29,
            "cognitive_effect_expected_string_error_count": 29,
            "terminal_semantics_recovered_or_used": False,
        },
        "post_reveal_fixtures": {
            lane: {
                "path": POST_REVEAL_FIXTURE_RELPATHS[lane],
                "validation_error_count": 0,
                "meaning_validated": False,
            }
            for lane in LANES
        },
        "conclusion": (
            "The prospective schema accepts the known-valid scalar envelope "
            "and rejects every one of the 29 historical array-shaped "
            "cognitive_effect fields. This proves only the repaired shape "
            "boundary."
        ),
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }


def _build_contract(
    *,
    generated_refs: Mapping[str, Mapping[str, Any]],
    schema_refs: Mapping[str, Mapping[str, Any]],
    post_schema_refs: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": (
            "lolla.product_delta_agent_graph_review_envelope_repair_contract.v1"
        ),
        "repair_id": REPAIR_ID,
        "date": DATE,
        "status": (
            "provider_free_repair_complete_"
            "semantic_execution_not_authorized"
        ),
        "owner": "existing_offline_product_delta_evaluation",
        "falsifiable_question": (
            "Can one authoritative structured-output schema remove the known "
            "scalar-versus-array ambiguity while preserving the exact frozen "
            "review material and without changing graph behavior?"
        ),
        "one_allowed_causal_change": (
            "Replace the reviewer-facing example shape with one checked-in "
            "JSON Schema passed to Codex through --output-schema, followed by "
            "the existing deterministic Product Delta admission checks."
        ),
        "provider_free_result": (
            "The known-valid scalar fixture passes and the exact historical "
            "29-array failure pattern is rejected at 29 cognitive_effect "
            "paths. No semantic context was started."
        ),
        "why_reuse_frozen_answers": (
            "The next run, if separately authorized, is a reviewer-envelope "
            "repair rather than another generation experiment. Reusing all "
            "eight frozen admitted answers holds the source, graph increment, "
            "answer variation, comparison orientation, and controls fixed. "
            "Generating new answers would confound the envelope change with "
            "new reasoner variation."
        ),
        "why_both_blind_reviews_rerun": (
            "A corrected skeptical-only response would be a selective retry "
            "after observing one valid primary result. Two fresh isolated "
            "reviewers must instead receive the same v2 boundary symmetrically. "
            "Neither historical review is promoted into the v2 pair."
        ),
        "input_locks": {
            relpath: {
                "path": relpath,
                **copy.deepcopy(metadata),
            }
            for relpath, metadata in FROZEN_INPUT_LOCKS.items()
        },
        "generated_provider_free_artifacts": {
            relpath: copy.deepcopy(dict(ref))
            for relpath, ref in generated_refs.items()
        },
        "structured_output_support": {
            "checked_on": DATE,
            "installed_cli_observed": "codex-cli 0.144.5",
            "installed_cli_help_exposed_output_schema": True,
            "official_guidance": (
                "https://learn.chatgpt.com/docs/non-interactive-mode.md"
            ),
            "official_guidance_summary": (
                "Codex non-interactive mode documents --output-schema for a "
                "final response conforming to supplied JSON Schema."
            ),
            "portability_claim": False,
            "future_execution_must_recheck_current_cli_and_official_guidance": (
                True
            ),
        },
        "current_authorization": {
            "provider_free_schema_packet_fixture_and_documentation_work": True,
            "new_codex_semantic_contexts": 0,
            "new_codex_semantic_execution_authorized": False,
            "repository_provider_api_calls": 0,
            "repository_provider_api_cost_usd": 0.0,
            "private_archive_inspection": False,
            "principal_human_fields": False,
            "historical_review_repair": False,
            "graph_source_or_relation_change": False,
            "graph_traversal_or_policy_change": False,
            "planner_compiler_runtime_or_skill_change": False,
            "answer_quality_or_usefulness_claim": False,
        },
        "proposed_next_run": {
            "authorized_now": False,
            "exact_authorization_required": EXACT_AUTHORIZATION,
            "generation_contexts": 0,
            "blind_review_contexts": 2,
            "conditional_post_reveal_contexts": 2,
            "maximum_codex_contexts": 4,
            "repository_provider_api_calls": 0,
            "repository_provider_api_cost_ceiling_usd": 0.0,
            "codex_platform_route_token_and_economic_cost": (
                "unavailable_to_repository_operator_not_claimed_zero"
            ),
            "reuse_frozen_generation_outputs": True,
            "reuse_historical_blind_reviews_as_v2_results": False,
            "review_lanes": list(LANES),
            "run_both_blind_contexts_even_if_one_fails": True,
            "post_reveal_start_gate": (
                "both new blind reviews must have valid first-terminal "
                "results under their lane schema and existing Product Delta "
                "validator"
            ),
            "retry_fallback_healing_replacement_reformatting": False,
            "semantic_salvage_from_invalid_payload": False,
            "blind_execution_envelopes": {
                lane: {
                    "stdin_packet": PACKET_RELPATHS[lane],
                    "output_schema": copy.deepcopy(
                        dict(schema_refs[lane])
                    ),
                    "first_terminal_output": FUTURE_REVIEW_RELPATHS[lane],
                    "first_terminal_failure_receipt": (
                        FUTURE_REVIEW_FAILURE_RELPATHS[lane]
                    ),
                    "argv_template": _codex_argv_template(
                        schema_relpath=SCHEMA_RELPATHS[lane],
                    ),
                }
                for lane in LANES
            },
            "conditional_post_reveal_envelopes": {
                lane: {
                    "packet_path_after_gate": (
                        FUTURE_POST_REVEAL_PACKET_RELPATHS[lane]
                    ),
                    "output_schema": copy.deepcopy(
                        dict(post_schema_refs[lane])
                    ),
                    "first_terminal_output": (
                        FUTURE_INTERPRETATION_RELPATHS[lane]
                    ),
                    "argv_template": _codex_argv_template(
                        schema_relpath=POST_REVEAL_SCHEMA_RELPATHS[lane],
                    ),
                }
                for lane in LANES
            },
            "predeclared_consolidation": FUTURE_CONSOLIDATION_RELPATH,
            "predeclared_result_note": FUTURE_RESULT_RELPATH,
        },
        "admission_layers": [
            "Codex --output-schema generation-boundary constraint",
            "local conservative JSON-Schema-subset validation",
            "existing Product Delta exact case/order/enum validator",
            "first-terminal and failure custody without repair",
        ],
        "non_claims": [
            "not a semantic rerun or corrected historical review",
            "not graph causation relevance correctness value or usefulness evidence",
            "not proof that a schema-valid future review will be semantically wise",
            "not expected model behavior or a provider/model comparison",
            "not principal-human review or F2/F3 completion",
            (
                "not permission to change incoming edges hop depth reserve "
                "ranking or traversal"
            ),
            (
                "not a live graph planner compiler skill Decision Work Atlas "
                "Observatory or interface change"
            ),
        ],
        "stop_rules": [
            "stop_if_any_frozen_replication_input_hash_or_byte_count_drifts",
            (
                "stop_if_source_answers_controls_comparison_orientation_or_"
                "review_grammar_changes"
            ),
            "stop_before_any_semantic_context_without_the_exact_new_authorization",
            "stop_if_current_codex_cli_no_longer_supports_output_schema",
            "run_both_blind_lanes_once_and_preserve_each_first_terminal_state",
            (
                "do_not_retry_repair_reformat_replace_or_semantically_salvage_"
                "an_invalid_terminal_payload"
            ),
            "do_not_start_post_reveal_unless_both_new_blind_reviews_are_valid",
            "stop_if_any_context_sees_sibling_work_or_lineage_before_its_declared_gate",
            (
                "stop_before_any_provider_api_private_archive human-field "
                "graph runtime or interface change"
            ),
            "do_not_report_shape_validity_as_semantic_correctness_or graph value",
        ],
    }


def _adapt_historical_review_fixture(
    payload: Mapping[str, Any], *, review_id: str
) -> dict[str, Any]:
    fixture = copy.deepcopy(dict(payload))
    fixture["schema_version"] = REVIEW_SCHEMA_VERSION
    fixture["review_id"] = review_id
    return fixture


def _build_post_reveal_fixture(*, lane: str) -> dict[str, Any]:
    return {
        "schema_version": POST_REVEAL_SCHEMA_VERSION,
        "interpretation_id": INTERPRETATION_IDS[lane],
        "source_review_id": REVIEW_IDS[lane],
        "fresh_post_reveal_context": True,
        "saw_sibling_review_or_interpretation": False,
        "state": "review_specific_pattern_mixed_or_uncertain",
        "pair_assessments": [
            {
                "case_id": case_id,
                "sealed_pair_role": (
                    "within_condition" if index < 4 else "cross_condition"
                ),
                "frozen_material_decision_difference": "uncertain",
                "cited_frozen_move_ids": [],
                "recurrence_observation": "shape fixture only",
                "burden_harm_or_lost_value_observation": (
                    "shape fixture only"
                ),
                "uncertainty": "shape fixture only",
            }
            for index, case_id in enumerate(COMPARISON_CASE_IDS)
        ],
        "rationale": "Shape fixture only; no semantic interpretation.",
        "nonclaims_acknowledged": list(NON_CLAIMS),
    }


def _review_task_wrapper(*, lane: str) -> str:
    return (
        "Run one isolated blind Product Delta review using only this packet. "
        "Do not inspect the repository, condition lineage, prior results, or "
        "sibling work. Complete every qualification, duplicate, comparison, "
        "and stand-down record in the declared order. Use one to four concise "
        "atomic moves per available comparison. The JSON Schema supplied by "
        "the execution boundary through --output-schema is the sole response-"
        "shape authority. Every enum-valued field, especially "
        "cognitive_effect, must contain exactly one JSON string and never an "
        f"array. Use review_id {REVIEW_IDS[lane]!r}. Return one JSON object "
        "and no markdown. Do not score, rank, vote, select a winner, infer "
        "graph lineage, or claim answer quality or usefulness."
    )


def _codex_argv_template(*, schema_relpath: str) -> list[str]:
    return [
        "codex",
        "exec",
        "--ephemeral",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "--color",
        "never",
        "-C",
        "{fresh_external_temporary_directory}",
        "--output-schema",
        f"{{repository_root}}/{schema_relpath}",
        "-o",
        "{external_first_terminal_output_path}",
        "-",
    ]


def _load_locked_inputs(root: Path) -> dict[str, Any]:
    payloads: dict[str, Any] = {}
    for relpath, expected in FROZEN_INPUT_LOCKS.items():
        path = _resolve_repo_path(root, relpath)
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise ProductDeltaGraphReviewEnvelopeV2Error(
                f"missing frozen input:{relpath}"
            ) from exc
        if len(raw) != expected["bytes"]:
            raise ProductDeltaGraphReviewEnvelopeV2Error(
                f"frozen input byte drift:{relpath}"
            )
        if hashlib.sha256(raw).hexdigest() != expected["sha256"]:
            raise ProductDeltaGraphReviewEnvelopeV2Error(
                f"frozen input hash drift:{relpath}"
            )
        try:
            payloads[relpath] = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ProductDeltaGraphReviewEnvelopeV2Error(
                f"frozen input JSON invalid:{relpath}"
            ) from exc
    return payloads


def _assert_semantic_inputs_preserved(
    *, packet: Mapping[str, Any], blind: Mapping[str, Any]
) -> None:
    for key in (
        "authoritative_source",
        "review_order",
        "visibility",
        "qualification_cases",
        "exact_duplicate_null",
        "comparison_case_count",
        "comparison_cases",
        "standdown_cases",
        "pre_review_mechanical_availability",
        "non_claims",
    ):
        if packet.get(key) != blind.get(key):
            raise ProductDeltaGraphReviewEnvelopeV2Error(
                f"semantic review material drifted:{key}"
            )


def _assert_no_ambiguous_shape(packet: Mapping[str, Any]) -> None:
    rendered = render_json(packet)
    for forbidden in (
        '"available_pair_response_shape"',
        '"qualification_response_shape"',
        '"standdown_response_shape"',
        '"response_envelope_contract"',
        '"fresh_context_task_wrappers"',
    ):
        if forbidden in rendered:
            raise ProductDeltaGraphReviewEnvelopeV2Error(
                f"ambiguous v1 response shape survived:{forbidden}"
            )


def _closed_object(properties: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": copy.deepcopy(dict(properties)),
        "required": list(properties),
        "additionalProperties": False,
    }


def _string_array() -> dict[str, Any]:
    return {"type": "array", "items": {"type": "string"}}


def _fixed_array(item_schema: Mapping[str, Any], count: int) -> dict[str, Any]:
    return {
        "type": "array",
        "items": copy.deepcopy(dict(item_schema)),
        "minItems": count,
        "maxItems": count,
    }


def _enum_string(values: Sequence[str]) -> dict[str, Any]:
    return {"type": "string", "enum": list(values)}


def _enum_boolean(value: bool) -> dict[str, Any]:
    return {"type": "boolean", "enum": [value]}


def _matches_json_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, Mapping)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def _case_ids(records: Sequence[Any]) -> list[str]:
    case_ids = [
        str(item.get("case_id"))
        for item in records
        if isinstance(item, Mapping) and item.get("case_id")
    ]
    if len(case_ids) != len(records) or len(case_ids) != len(set(case_ids)):
        raise ProductDeltaGraphReviewEnvelopeV2Error(
            "case identity set is malformed"
        )
    return case_ids


def _required_mapping(
    value: Mapping[str, Any], key: str
) -> Mapping[str, Any]:
    result = value.get(key)
    if not isinstance(result, Mapping):
        raise ProductDeltaGraphReviewEnvelopeV2Error(
            f"required object missing:{key}"
        )
    return result


def _required_list(value: Mapping[str, Any], key: str) -> list[Any]:
    result = value.get(key)
    if not isinstance(result, list):
        raise ProductDeltaGraphReviewEnvelopeV2Error(
            f"required array missing:{key}"
        )
    return result


def _locked_ref(relpath: str) -> dict[str, Any]:
    return {
        "path": relpath,
        **copy.deepcopy(FROZEN_INPUT_LOCKS[relpath]),
    }


def _ref_for_payload(
    relpath: str, payload: Mapping[str, Any]
) -> dict[str, Any]:
    raw = render_json(payload).encode("utf-8")
    return {
        "path": relpath,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def _resolve_repo_path(root: Path, relpath: str) -> Path:
    target = (root / relpath).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ProductDeltaGraphReviewEnvelopeV2Error(
            "repository-relative path escaped root"
        ) from exc
    return target
