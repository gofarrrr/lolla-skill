"""Build the provider-free V3 post-reveal nonclaim-custody repair.

This module deepens the existing offline Product Delta evaluator. It keeps the
two valid V2 blind reviews, deterministic lineage reveal, semantic response
fields, and local admission owner frozen. Its one prospective change moves the
ten experiment nonclaims out of the model-authored response and into exact
deterministic input-packet custody.

The module never invokes Codex or a provider, repairs historical payloads,
interprets semantic evidence, changes the graph, or authorizes a future run.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_graph_replication_result import (
    EXPECTED_INTERPRETATION_IDS as EXPECTED_V1_INTERPRETATION_IDS,
    EXPECTED_REVIEW_IDS as EXPECTED_V1_REVIEW_IDS,
    NON_CLAIMS,
    POST_REVEAL_INTERPRETATION_SCHEMA_VERSION as POST_REVEAL_V1,
    _validate_post_reveal_interpretation,
)
from engine.system_b.product_delta_graph_review_envelope_v2 import (
    FUTURE_POST_REVEAL_PACKET_RELPATHS as V2_POST_REVEAL_PACKET_RELPATHS,
    INTERPRETATION_IDS as V2_INTERPRETATION_IDS,
    LANES,
    POST_REVEAL_FIXTURE_RELPATHS as V2_FIXTURE_RELPATHS,
    POST_REVEAL_SCHEMA_RELPATHS as V2_SCHEMA_RELPATHS,
    REVIEW_IDS as V2_REVIEW_IDS,
    validate_json_schema_subset,
)


DATE = "2026-07-24"
REPAIR_ID = "lolla-agent-only-graph-review-nonclaim-custody-v3"
OUTPUT_DIR = (
    "research/agent-only-graph-review-nonclaim-custody-v3-2026-07-24"
)
FUTURE_REVIEW_DIR = (
    "reviews/codex-assisted/agent-only-graph-review-nonclaim-custody-v3"
)

POST_REVEAL_SCHEMA_VERSION = (
    "lolla.product_delta_graph_replication_post_reveal_interpretation.v3"
)
POST_REVEAL_PACKET_SCHEMA_VERSION = (
    "lolla.product_delta_graph_replication_post_reveal_packet.v3"
)
NONCLAIM_CUSTODY_SCHEMA_VERSION = (
    "lolla.product_delta_graph_review_nonclaim_input_custody.v1"
)

INTERPRETATION_IDS = {
    lane: f"agent-graph-review-nonclaim-custody-v3-pattern-{lane}"
    for lane in LANES
}
SCHEMA_RELPATHS = {
    lane: f"{OUTPUT_DIR}/schemas/post-reveal-{lane}.schema.json"
    for lane in LANES
}
PACKET_RELPATHS = {
    lane: f"{OUTPUT_DIR}/packets/post-reveal-{lane}.json"
    for lane in LANES
}
VALID_FIXTURE_RELPATHS = {
    lane: f"{OUTPUT_DIR}/fixtures/post-reveal-valid-{lane}.json"
    for lane in LANES
}
LEGACY_ECHO_FIXTURE_RELPATHS = {
    lane: f"{OUTPUT_DIR}/fixtures/post-reveal-legacy-echo-{lane}.json"
    for lane in LANES
}
FIXTURE_RECEIPT_RELPATH = f"{OUTPUT_DIR}/fixture-validation-receipt.json"
CONTRACT_RELPATH = (
    "docs/evals/"
    "lolla-agent-only-graph-review-nonclaim-custody-v3-contract-v1.json"
)
PLAN_RELPATH = (
    "plans/"
    "lolla-agent-only-graph-review-nonclaim-custody-v3-repair-2026-07-24.md"
)
RESULT_RELPATH = (
    "docs/conversation-understanding/"
    "lolla-agent-only-graph-review-nonclaim-custody-v3-repair-result-"
    "2026-07-24.md"
)

FUTURE_INTERPRETATION_RELPATHS = {
    lane: f"{FUTURE_REVIEW_DIR}/pattern-interpretation-{lane}.json"
    for lane in LANES
}
FUTURE_FAILURE_RELPATHS = {
    lane: (
        f"{FUTURE_REVIEW_DIR}/"
        f"pattern-interpretation-{lane}-terminal-failure.json"
    )
    for lane in LANES
}
FUTURE_CONSOLIDATION_RELPATH = f"{OUTPUT_DIR}/consolidated-diagnostic.json"
FUTURE_RESULT_RELPATH = (
    "docs/conversation-understanding/"
    "lolla-agent-only-graph-review-nonclaim-custody-v3-result-2026-07-24.md"
)

V2_CONTRACT_RELPATH = (
    "docs/evals/lolla-agent-only-graph-review-envelope-repair-contract-v1.json"
)
V2_CONSOLIDATION_RELPATH = (
    "research/agent-only-graph-review-envelope-repair-2026-07-24/"
    "consolidated-diagnostic.json"
)
V2_BLIND_REVIEW_RELPATHS = {
    lane: (
        "reviews/codex-assisted/agent-only-graph-review-envelope-v2/"
        f"pair-review-{lane}.json"
    )
    for lane in LANES
}
V2_POST_FAILURE_RELPATHS = {
    lane: (
        "reviews/codex-assisted/agent-only-graph-review-envelope-v2/"
        f"pattern-interpretation-{lane}-terminal-failure.json"
    )
    for lane in LANES
}

FROZEN_INPUT_LOCKS = {
    V2_CONTRACT_RELPATH: {
        "bytes": 16310,
        "sha256": (
            "4b43f0008912d472a0a4b118550c3034ae9f8e26ac4465d6cbe720a06054abd5"
        ),
    },
    V2_SCHEMA_RELPATHS["primary"]: {
        "bytes": 3297,
        "sha256": (
            "5cfc410892b6f6d97d72ae47cc58e5733f9c930792b0e1450bd4705a7844526c"
        ),
    },
    V2_SCHEMA_RELPATHS["skeptical"]: {
        "bytes": 3303,
        "sha256": (
            "83fe5e867256da7d186ab7e7ba99f8c816ad667c752e772420bb76e1c5b1ae8b"
        ),
    },
    V2_FIXTURE_RELPATHS["primary"]: {
        "bytes": 3932,
        "sha256": (
            "0e27edf780bbd0af15ce04f33834d90906260e00ce93113637eb2f80f0064ef6"
        ),
    },
    V2_FIXTURE_RELPATHS["skeptical"]: {
        "bytes": 3936,
        "sha256": (
            "588964cddb1fa32f9c61861cd7d65b694f02c60abe8af1517818c9977d49cd95"
        ),
    },
    V2_POST_REVEAL_PACKET_RELPATHS["primary"]: {
        "bytes": 75906,
        "sha256": (
            "88bfc70504f03fc9d137db7fa434391bdedb20d382618b6f6f11d2743997e3e1"
        ),
    },
    V2_POST_REVEAL_PACKET_RELPATHS["skeptical"]: {
        "bytes": 77557,
        "sha256": (
            "4d95805d7c56f4745c9bc0e2f329e1ea7c11d3f3c21ab628b81295f82ea23b50"
        ),
    },
    V2_BLIND_REVIEW_RELPATHS["primary"]: {
        "bytes": 49595,
        "sha256": (
            "7717938872cd52240a67f1f5fb46b396481a12e25433aaa811901302527d0c54"
        ),
    },
    V2_BLIND_REVIEW_RELPATHS["skeptical"]: {
        "bytes": 50686,
        "sha256": (
            "dda30d94f4fae03f39af249cd33be517236c1c930955936c33fb8166af770fc1"
        ),
    },
    V2_POST_FAILURE_RELPATHS["primary"]: {
        "bytes": 1379,
        "sha256": (
            "62a0788a4bbed4759db7e73253d08ea4c4ead8746955b128855bb2c22cf3dedc"
        ),
    },
    V2_POST_FAILURE_RELPATHS["skeptical"]: {
        "bytes": 1383,
        "sha256": (
            "66fc78806dfdc3ceb0a64d71f8bbffd3c5a3a1d9c46fae1bbdb4fe722de7e68b"
        ),
    },
    V2_CONSOLIDATION_RELPATH: {
        "bytes": 149817,
        "sha256": (
            "5d9d72645be12d17864c102b86336871387bce37b54a6e5ea98d789ca56fdf27"
        ),
    },
}

EXACT_FUTURE_AUTHORIZATION = (
    "AUTHORIZE_LOLLA_GRAPH_REVIEW_NONCLAIM_CUSTODY_V3: "
    "reuse_frozen_v2_blind_reviews=true; post_reveal_contexts=2; "
    "maximum_codex_contexts=2; repository_provider_api_calls=0; "
    "repository_provider_api_cost_usd=0.00; no_retry=true"
)


class ProductDeltaGraphReviewNonclaimCustodyV3Error(ValueError):
    """Sanitized deterministic V3 custody-repair failure."""


def render_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload, ensure_ascii=False, indent=2, sort_keys=True
    ) + "\n"


def nonclaim_statement_sha256(statements: Sequence[str]) -> str:
    serialized = json.dumps(
        list(statements),
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def build_artifacts(*, repo_root: Path | str) -> dict[str, dict[str, Any]]:
    """Build the complete provider-free prospective V3 package."""

    root = Path(repo_root).resolve()
    locked = _load_locked_inputs(root)
    schemas: dict[str, dict[str, Any]] = {}
    packets: dict[str, dict[str, Any]] = {}
    valid_fixtures: dict[str, dict[str, Any]] = {}
    legacy_fixtures: dict[str, dict[str, Any]] = {}

    for lane in LANES:
        schemas[lane] = _build_v3_schema(
            locked[V2_SCHEMA_RELPATHS[lane]],
            lane=lane,
        )
        schema_ref = _ref_for_payload(
            SCHEMA_RELPATHS[lane], schemas[lane]
        )
        packets[lane] = _build_v3_packet(
            locked[V2_POST_REVEAL_PACKET_RELPATHS[lane]],
            lane=lane,
            schema_ref=schema_ref,
        )
        valid_fixtures[lane], legacy_fixtures[lane] = _build_fixtures(
            locked[V2_FIXTURE_RELPATHS[lane]],
            lane=lane,
            packet=packets[lane],
        )

    receipt = _build_fixture_receipt(
        schemas=schemas,
        packets=packets,
        valid_fixtures=valid_fixtures,
        legacy_fixtures=legacy_fixtures,
    )
    artifacts: dict[str, dict[str, Any]] = {}
    for lane in LANES:
        artifacts[SCHEMA_RELPATHS[lane]] = schemas[lane]
        artifacts[PACKET_RELPATHS[lane]] = packets[lane]
        artifacts[VALID_FIXTURE_RELPATHS[lane]] = valid_fixtures[lane]
        artifacts[LEGACY_ECHO_FIXTURE_RELPATHS[lane]] = (
            legacy_fixtures[lane]
        )
    artifacts[FIXTURE_RECEIPT_RELPATH] = receipt
    generated_refs = {
        relpath: _ref_for_payload(relpath, payload)
        for relpath, payload in artifacts.items()
    }
    artifacts[CONTRACT_RELPATH] = _build_contract(
        generated_refs=generated_refs
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
    try:
        expected = build_artifacts(repo_root=root)
    except ProductDeltaGraphReviewNonclaimCustodyV3Error as exc:
        return [str(exc)]
    errors: list[str] = []
    for relpath, payload in expected.items():
        target = _resolve_repo_path(root, relpath)
        try:
            actual = target.read_text(encoding="utf-8")
        except OSError:
            errors.append(f"missing generated artifact:{relpath}")
            continue
        if actual != render_json(payload):
            errors.append(f"generated artifact drift:{relpath}")
    if not _resolve_repo_path(root, PLAN_RELPATH).is_file():
        errors.append(f"missing prospective plan:{PLAN_RELPATH}")
    if not _resolve_repo_path(root, RESULT_RELPATH).is_file():
        errors.append(f"missing provider-free result:{RESULT_RELPATH}")
    for relpath in (
        *FUTURE_INTERPRETATION_RELPATHS.values(),
        *FUTURE_FAILURE_RELPATHS.values(),
        FUTURE_CONSOLIDATION_RELPATH,
        FUTURE_RESULT_RELPATH,
    ):
        if _resolve_repo_path(root, relpath).exists():
            errors.append(f"unauthorized semantic result exists:{relpath}")
    return errors


def validate_nonclaim_custody(packet: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    custody = packet.get("nonclaim_custody")
    if not isinstance(custody, Mapping):
        return ["nonclaim custody is missing"]
    if custody.get("schema_version") != NONCLAIM_CUSTODY_SCHEMA_VERSION:
        errors.append("nonclaim custody schema drifted")
    if custody.get("owner") != "deterministic_input_packet":
        errors.append("nonclaim custody owner drifted")
    if custody.get("statement_count") != len(NON_CLAIMS):
        errors.append("nonclaim custody statement count drifted")
    expected_statements = [
        {
            "nonclaim_id": f"NC-{index:02d}",
            "text": statement,
        }
        for index, statement in enumerate(NON_CLAIMS, start=1)
    ]
    if custody.get("statements") != expected_statements:
        errors.append("nonclaim custody statements drifted")
    observed_statements = custody.get("statements")
    observed_texts = (
        [
            str(row.get("text"))
            for row in observed_statements
            if isinstance(row, Mapping)
        ]
        if isinstance(observed_statements, list)
        else []
    )
    stored_hash = custody.get("ordered_statement_sha256")
    if (
        len(observed_texts) != len(NON_CLAIMS)
        or stored_hash != nonclaim_statement_sha256(observed_texts)
        or stored_hash != nonclaim_statement_sha256(NON_CLAIMS)
    ):
        errors.append("nonclaim custody statement hash drifted")
    if custody.get("model_response_echo_required") is not False:
        errors.append("model response echo boundary drifted")
    if custody.get("proves_input_presentation") is not True:
        errors.append("input presentation claim drifted")
    if custody.get("proves_internal_compliance") is not False:
        errors.append("internal compliance nonclaim drifted")
    return errors


def validate_v3_post_reveal(
    payload: Mapping[str, Any],
    *,
    packet: Mapping[str, Any],
    lane: str,
    schema: Mapping[str, Any],
) -> list[str]:
    """Validate V3 shape plus the existing Product Delta semantic boundary."""

    if lane not in LANES:
        return ["unknown review lane"]
    errors = validate_json_schema_subset(payload, schema)
    errors.extend(validate_nonclaim_custody(packet))
    adapted = copy.deepcopy(dict(payload))
    adapted["schema_version"] = POST_REVEAL_V1
    adapted["interpretation_id"] = EXPECTED_V1_INTERPRETATION_IDS[lane]
    adapted["source_review_id"] = EXPECTED_V1_REVIEW_IDS[lane]
    errors.extend(
        _validate_post_reveal_interpretation(
            adapted,
            packet=packet,
            expected_id=EXPECTED_V1_INTERPRETATION_IDS[lane],
            expected_review_id=EXPECTED_V1_REVIEW_IDS[lane],
            require_nonclaim_echo=False,
        )
    )
    return errors


def _build_v3_schema(
    source: Mapping[str, Any], *, lane: str
) -> dict[str, Any]:
    schema = copy.deepcopy(dict(source))
    properties = schema.get("properties")
    required = schema.get("required")
    if not isinstance(properties, dict) or not isinstance(required, list):
        raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
            "frozen V2 schema is malformed"
        )
    properties.pop("nonclaims_acknowledged", None)
    schema["required"] = [
        key for key in required if key != "nonclaims_acknowledged"
    ]
    schema["title"] = (
        f"Lolla graph review nonclaim-custody post-reveal v3 ({lane})"
    )
    schema["properties"]["schema_version"] = {
        "type": "string",
        "enum": [POST_REVEAL_SCHEMA_VERSION],
    }
    schema["properties"]["interpretation_id"] = {
        "type": "string",
        "enum": [INTERPRETATION_IDS[lane]],
    }
    schema["properties"]["source_review_id"] = {
        "type": "string",
        "enum": [V2_REVIEW_IDS[lane]],
    }
    return schema


def _build_v3_packet(
    source: Mapping[str, Any],
    *,
    lane: str,
    schema_ref: Mapping[str, Any],
) -> dict[str, Any]:
    packet = copy.deepcopy(dict(source))
    packet["schema_version"] = POST_REVEAL_PACKET_SCHEMA_VERSION
    packet["result_id"] = REPAIR_ID
    packet["repair_id"] = REPAIR_ID
    packet["status"] = (
        "prospective_v3_nonclaim_input_custody_"
        "semantic_execution_not_authorized"
    )
    packet["purpose"] = (
        "Interpret recurrence only inside the already-frozen V2 blind review. "
        "The response does not restate nonclaims; deterministic packet custody "
        "owns their exact presentation."
    )
    input_refs = packet.get("input_refs")
    if not isinstance(input_refs, dict):
        raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
            "frozen V2 post-reveal packet input refs are malformed"
        )
    input_refs["source_v2_post_reveal_packet"] = _locked_ref(
        V2_POST_REVEAL_PACKET_RELPATHS[lane]
    )
    input_refs["source_v2_post_reveal_schema"] = _locked_ref(
        V2_SCHEMA_RELPATHS[lane]
    )
    input_refs["source_v2_blind_review"] = _locked_ref(
        V2_BLIND_REVIEW_RELPATHS[lane]
    )
    structured = packet.get("structured_output_contract")
    if not isinstance(structured, dict):
        raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
            "frozen V2 structured output contract is malformed"
        )
    structured["authoritative_schema"] = copy.deepcopy(dict(schema_ref))
    structured["model_authored_nonclaim_echo_present"] = False
    structured["deterministic_input_custody_owns_nonclaims"] = True
    structured["schema_proves_nonclaim_compliance"] = False
    packet["task_wrapper"] = _task_wrapper(lane=lane)
    packet.pop("non_claims", None)
    packet["nonclaim_custody"] = _build_nonclaim_custody()
    if validate_nonclaim_custody(packet):
        raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
            "generated V3 nonclaim custody failed"
        )
    return packet


def _build_fixtures(
    source: Mapping[str, Any],
    *,
    lane: str,
    packet: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    legacy = copy.deepcopy(dict(source))
    legacy["schema_version"] = POST_REVEAL_SCHEMA_VERSION
    legacy["interpretation_id"] = INTERPRETATION_IDS[lane]
    legacy["source_review_id"] = V2_REVIEW_IDS[lane]
    reveal_rows = packet.get("comparison_reveal")
    assessments = legacy.get("pair_assessments")
    if not isinstance(reveal_rows, list) or not isinstance(assessments, list):
        raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
            "frozen V2 fixture or reveal rows are malformed"
        )
    reveal_by_id = {
        row.get("case_id"): row
        for row in reveal_rows
        if isinstance(row, Mapping)
    }
    for assessment in assessments:
        if not isinstance(assessment, dict):
            raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
                "frozen V2 fixture assessment is malformed"
            )
        reveal = reveal_by_id.get(assessment.get("case_id"))
        if not isinstance(reveal, Mapping):
            raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
                "frozen V2 fixture assessment has no reveal row"
            )
        assessment["sealed_pair_role"] = reveal["sealed_pair_role"]
        assessment["frozen_material_decision_difference"] = reveal[
            "frozen_material_decision_difference"
        ]
    valid = copy.deepcopy(legacy)
    valid.pop("nonclaims_acknowledged", None)
    return valid, legacy


def _build_nonclaim_custody() -> dict[str, Any]:
    return {
        "schema_version": NONCLAIM_CUSTODY_SCHEMA_VERSION,
        "owner": "deterministic_input_packet",
        "statement_count": len(NON_CLAIMS),
        "statements": [
            {
                "nonclaim_id": f"NC-{index:02d}",
                "text": statement,
            }
            for index, statement in enumerate(NON_CLAIMS, start=1)
        ],
        "ordered_statement_sha256": nonclaim_statement_sha256(NON_CLAIMS),
        "model_response_echo_required": False,
        "proves_input_presentation": True,
        "proves_internal_compliance": False,
        "claim_boundary": (
            "This custody block proves which exact nonclaims are present in "
            "the deterministic input packet. It does not prove that a model "
            "understood, followed, or semantically honored them."
        ),
    }


def _build_fixture_receipt(
    *,
    schemas: Mapping[str, Mapping[str, Any]],
    packets: Mapping[str, Mapping[str, Any]],
    valid_fixtures: Mapping[str, Mapping[str, Any]],
    legacy_fixtures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    valid_errors = {
        lane: validate_v3_post_reveal(
            valid_fixtures[lane],
            packet=packets[lane],
            lane=lane,
            schema=schemas[lane],
        )
        for lane in LANES
    }
    legacy_errors = {
        lane: validate_json_schema_subset(
            legacy_fixtures[lane], schemas[lane]
        )
        for lane in LANES
    }
    custody_errors = {
        lane: validate_nonclaim_custody(packets[lane]) for lane in LANES
    }
    if any(valid_errors.values()):
        raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
            "V3 valid fixture failed"
        )
    expected_legacy_error = [
        "$:unexpected property nonclaims_acknowledged"
    ]
    if any(
        legacy_errors[lane] != expected_legacy_error for lane in LANES
    ):
        raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
            "legacy response echo was not rejected exactly"
        )
    if any(custody_errors.values()):
        raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
            "V3 packet nonclaim custody failed"
        )
    return {
        "schema_version": (
            "lolla.product_delta_graph_review_nonclaim_custody_"
            "fixture_receipt.v1"
        ),
        "repair_id": REPAIR_ID,
        "date": DATE,
        "status": (
            "provider_free_nonclaim_input_custody_fixture_gate_passed"
        ),
        "evidence_class": (
            "development_contract_fixture_not_semantic_graph_or_"
            "usefulness_evidence"
        ),
        "valid_fixture_count": len(LANES),
        "valid_fixture_error_count": 0,
        "legacy_echo_rejection_count": len(LANES),
        "legacy_echo_error_per_fixture": (
            "$:unexpected property nonclaims_acknowledged"
        ),
        "input_nonclaim_custody_error_count": 0,
        "semantic_correctness_validated": False,
        "model_compliance_validated": False,
        "graph_value_validated": False,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }


def _build_contract(
    *, generated_refs: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    return {
        "schema_version": (
            "lolla.product_delta_graph_review_nonclaim_custody_"
            "repair_contract.v1"
        ),
        "repair_id": REPAIR_ID,
        "date": DATE,
        "status": (
            "provider_free_nonclaim_custody_repair_complete_"
            "semantic_execution_not_authorized"
        ),
        "owner": "existing_offline_product_delta_evaluation",
        "falsifiable_question": (
            "Can deterministic input-packet custody preserve the exact ten "
            "post-reveal nonclaims while the model-authored response omits "
            "every nonclaim echo field?"
        ),
        "one_allowed_causal_change": (
            "Move the ten exact nonclaims from a model-authored response echo "
            "into stable-ID deterministic input-packet custody. Preserve the "
            "two valid V2 blind reviews, lineage reveal, response semantics, "
            "and existing Product Delta admission behavior."
        ),
        "decision": (
            "Input-side deterministic custody owns exact nonclaim "
            "presentation. No boolean or free-text model acknowledgment is "
            "treated as proof of compliance."
        ),
        "why_not_boolean_acknowledgments": (
            "A schema-forced true value would prove only that the generated "
            "shape contained true. It would not establish that the model "
            "understood or followed the nonclaim."
        ),
        "frozen_v2_input_locks": {
            relpath: {"path": relpath, **copy.deepcopy(metadata)}
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
            "official_manual_section": (
                "Create structured outputs with a schema"
            ),
            "official_guidance_summary": (
                "Codex exec --output-schema requests a final response "
                "conforming to supplied JSON Schema, and -o writes the final "
                "message."
            ),
            "schema_proves_shape_not_semantic_compliance": True,
            "future_execution_must_recheck_cli_and_official_guidance": True,
        },
        "current_authorization": {
            "provider_free_contract_fixture_and_documentation_work": True,
            "new_codex_semantic_contexts": 0,
            "new_codex_semantic_execution_authorized": False,
            "repository_provider_api_calls": 0,
            "repository_provider_api_cost_usd": 0.0,
            "private_archive_inspection": False,
            "principal_human_fields": False,
            "historical_payload_repair_or_semantic_salvage": False,
            "graph_source_relation_traversal_policy_or_runtime_change": False,
            "answer_quality_graph_value_or_usefulness_claim": False,
        },
        "prospective_run": {
            "authorized_now": False,
            "exact_authorization_required": EXACT_FUTURE_AUTHORIZATION,
            "reuse_frozen_v2_blind_reviews": True,
            "generation_contexts": 0,
            "blind_review_contexts": 0,
            "post_reveal_contexts": 2,
            "maximum_codex_contexts": 2,
            "repository_provider_api_calls": 0,
            "repository_provider_api_cost_ceiling_usd": 0.0,
            "no_retry": True,
            "run_both_lanes_once_even_if_one_fails": True,
            "retry_fallback_healing_replacement_reformatting": False,
            "semantic_salvage_from_invalid_payload": False,
            "codex_platform_route_tokens_and_economic_cost": (
                "unavailable_to_repository_operator_not_claimed_zero"
            ),
            "lane_envelopes": {
                lane: {
                    "stdin_packet": PACKET_RELPATHS[lane],
                    "output_schema": SCHEMA_RELPATHS[lane],
                    "first_terminal_output": (
                        FUTURE_INTERPRETATION_RELPATHS[lane]
                    ),
                    "first_terminal_failure": FUTURE_FAILURE_RELPATHS[lane],
                    "argv_template": _codex_argv_template(
                        schema_relpath=SCHEMA_RELPATHS[lane]
                    ),
                }
                for lane in LANES
            },
            "predeclared_consolidation": FUTURE_CONSOLIDATION_RELPATH,
            "predeclared_result_note": FUTURE_RESULT_RELPATH,
        },
        "provider_free_result": {
            "valid_v3_fixture_count": 2,
            "legacy_echo_fixture_rejection_count": 2,
            "nonclaim_input_custody_error_count": 0,
            "semantic_contexts_started": 0,
            "meaning_validated": False,
            "model_compliance_validated": False,
            "graph_value_validated": False,
        },
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "non_claims": [
            "not a corrected V2 terminal payload or semantic salvage",
            "not a V3 semantic run or authorization",
            "not proof that a model followed the supplied nonclaims",
            "not graph causation relevance correctness value or usefulness evidence",
            "not proof that either condition or answer is better",
            "not expected model behavior or a provider/model comparison",
            "not principal-human review or F2/F3 completion",
            "not permission to change graph traversal policy or runtime",
        ],
        "stop_rules": [
            "stop_if_any_frozen_v2_input_byte_count_or_hash_drifts",
            "stop_if_any_semantic_response_field_other_than_nonclaim_echo_changes",
            "stop_before_any_codex_context_without_exact_new_authorization",
            "stop_before_any_provider_api_private_archive or human-field work",
            "stop_before_any graph source relation traversal policy runtime or interface change",
            "do_not_report_input_custody_as_internal_model_compliance",
            "do_not_report_schema_validity_as semantic correctness or graph value",
        ],
    }


def _task_wrapper(*, lane: str) -> str:
    return (
        "Run one isolated post-reveal interpretation over exactly the frozen "
        "V2 blind review in this packet. Address all eight comparisons in "
        "order and cite only frozen move IDs. Do not add or change answer "
        "judgments, inspect or infer a sibling review, score, rank, vote, "
        "choose a winner, or claim graph causation, answer quality, expected "
        "behavior, or usefulness. The deterministic nonclaim_custody block "
        "states the exact experiment limits and is input custody, not a field "
        "to repeat. The JSON Schema supplied through --output-schema is the "
        "sole response-shape authority. Return exactly one JSON object with "
        f"interpretation_id {INTERPRETATION_IDS[lane]!r}, source_review_id "
        f"{V2_REVIEW_IDS[lane]!r}, and no markdown."
    )


def _codex_argv_template(*, schema_relpath: str) -> list[str]:
    return [
        "codex",
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--output-schema",
        f"{{repository_root}}/{schema_relpath}",
        "-o",
        "{external_first_terminal_output_path}",
        "-",
    ]


def _load_locked_inputs(root: Path) -> dict[str, dict[str, Any]]:
    locked: dict[str, dict[str, Any]] = {}
    for relpath, expected in FROZEN_INPUT_LOCKS.items():
        target = _resolve_repo_path(root, relpath)
        try:
            raw = target.read_bytes()
        except OSError as exc:
            raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
                f"missing frozen V2 input:{relpath}"
            ) from exc
        if len(raw) != expected["bytes"]:
            raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
                f"frozen V2 input byte count drifted:{relpath}"
            )
        if hashlib.sha256(raw).hexdigest() != expected["sha256"]:
            raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
                f"frozen V2 input hash drifted:{relpath}"
            )
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
                f"frozen V2 input is not JSON:{relpath}"
            ) from exc
        if not isinstance(payload, dict):
            raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
                f"frozen V2 input is not an object:{relpath}"
            )
        locked[relpath] = payload
    return locked


def _locked_ref(relpath: str) -> dict[str, Any]:
    metadata = FROZEN_INPUT_LOCKS[relpath]
    return {
        "path": relpath,
        "bytes": metadata["bytes"],
        "sha256": metadata["sha256"],
    }


def _ref_for_payload(
    relpath: str, payload: Mapping[str, Any]
) -> dict[str, Any]:
    raw = render_json(payload).encode("utf-8")
    return {
        "path": relpath,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def _resolve_repo_path(root: Path, relpath: str) -> Path:
    target = (root / relpath).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ProductDeltaGraphReviewNonclaimCustodyV3Error(
            "path escapes repository root"
        ) from exc
    return target
