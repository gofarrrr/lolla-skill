#!/usr/bin/env python3
"""Build the provider-free matched R4 residual-contract holdout package."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from collections.abc import Sequence
from typing import Any

from engine.system_b.conversation_state_fan_in import build_source_registry
from engine.system_b.r4_complementary_readers import (
    UNCERTAINTY_PACKET_SCHEMA,
    canonical_json_bytes,
    uncertainty_response_schema_v1,
    value_sha256,
)
from engine.system_b.r4_residual_task import (
    build_residual_prompts_v1,
    residual_response_schema_v1,
)
from engine.system_b.r4_semantic_distinction import build_uncertainty_prompts_v2


ROOT = Path(__file__).resolve().parents[2]
INPUT_ROOT = ROOT / "research/lolla-r4-matched-residual-holdout-source-freeze-2026-07-14"
TARGET = ROOT / "docs/evals/lolla-r4-matched-residual-holdout-target-v1.json"
PRACTICE = ROOT / "docs/conversation-understanding/lolla-r4-matched-residual-holdout-current-practice-2026-07-14.md"
RUNNER = ROOT / "scripts/evals/run_r4_matched_residual_holdout_experiment.py"
DEFAULT_OUTPUT = ROOT / "research/lolla-r4-matched-residual-holdout-contract-2026-07-14"
CONTRACT_RELATIVE = "docs/evals/lolla-r4-matched-residual-holdout-contract-v1.json"
CASE_IDS = (
    "r4h-case01-oral-history-release",
    "r4h-case02-serialized-audio-pilot",
    "r4h-case03-research-data-stewardship",
    "r4h-case04-cross-campus-language-program",
)
SEEDS = {
    "r4h-case01-oral-history-release": 9101,
    "r4h-case02-serialized-audio-pilot": 9201,
    "r4h-case03-research-data-stewardship": 9301,
    "r4h-case04-cross-campus-language-program": 9401,
}
PROVIDER = {
    "allow_fallbacks": False,
    "data_collection": "deny",
    "max_price": {"completion": 1.5, "prompt": 0.25},
    "only": ["google-vertex"],
    "order": ["google-vertex"],
    "require_parameters": True,
    "zdr": True,
}


class R4MatchedResidualHoldoutError(RuntimeError):
    """Raised when the matched holdout package or custody drifts."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4MatchedResidualHoldoutError(f"expected JSON object: {path}")
    return value


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _render(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def load_frozen_case_inputs() -> dict[str, dict[str, Any]]:
    """Load the four source/prior pairs and expose their exact artifact hashes."""

    result: dict[str, dict[str, Any]] = {}
    for case_id in CASE_IDS:
        source_path = INPUT_ROOT / "sources" / f"{case_id}.json"
        prior_path = INPUT_ROOT / "priors" / f"{case_id}.json"
        source = _load(source_path)
        prior = _load(prior_path)
        if source.get("case_id") != case_id or prior.get("case_id") != case_id:
            raise R4MatchedResidualHoldoutError(f"case identity drifted: {case_id}")
        result[case_id] = {
            "source": source,
            "prior": prior,
            "source_path": str(source_path.relative_to(ROOT)),
            "prior_path": str(prior_path.relative_to(ROOT)),
            "source_sha256": _file_sha(source_path),
            "prior_sha256": _file_sha(prior_path),
        }
    return result


def load_source_first_targets() -> dict[str, Any]:
    """Load review-only source-first targets after verifying the input freeze."""

    target = _load(TARGET)
    inputs = load_frozen_case_inputs()
    rows = target.get("cases")
    if not isinstance(rows, list) or [row.get("case_id") for row in rows] != list(
        CASE_IDS
    ):
        raise R4MatchedResidualHoldoutError("source-first target identity drifted")
    freeze = target.get("source_prior_freeze_manifest", {})
    freeze_path = ROOT / str(freeze.get("path", ""))
    if not freeze_path.is_file() or _file_sha(freeze_path) != freeze.get("sha256"):
        raise R4MatchedResidualHoldoutError("source/prior freeze manifest drifted")
    for row in rows:
        case = inputs[str(row["case_id"])]
        if (
            row.get("source_sha256") != case["source_sha256"]
            or row.get("prior_sha256") != case["prior_sha256"]
        ):
            raise R4MatchedResidualHoldoutError(
                f"source-first target input drifted: {row['case_id']}"
            )
    return target


def _packet(case: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    source = case["source"]
    prior = case["prior"]
    aliases = []
    registry_aliases = []
    for row in source["messages"]:
        message_index = int(row["message_index"])
        alias = f"e{message_index:03d}"
        text = str(row["text"])
        text_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        turn_index = (message_index + 1) // 2
        aliases.append(
            {
                "alias": alias,
                "speaker": row["speaker"],
                "text": text,
                "text_sha256": text_sha,
                "turn_index": turn_index,
            }
        )
        registry_aliases.append(
            {
                "alias": alias,
                "span_id": f"span-{source['case_id']}-{message_index:03d}",
                "speaker": row["speaker"],
                "text_sha256": text_sha,
                "turn_index": turn_index,
            }
        )
    source_path = str(case["source_path"])
    source_bytes = (ROOT / source_path).read_bytes()
    registry = build_source_registry(
        case_id=str(source["case_id"]),
        source_path=source_path,
        source_bytes=source_bytes,
        message_count=int(source["message_count"]),
        aliases=registry_aliases,
    )
    packet_body = {
        "schema_version": UNCERTAINTY_PACKET_SCHEMA,
        "status": "provider_free_matched_holdout_input_frozen",
        "case_id": source["case_id"],
        "source": {
            "path": source_path,
            "sha256": case["source_sha256"],
            "message_count": source["message_count"],
            "aliases": aliases,
        },
        "prior_interpretation_context": {
            "artifact_path": case["prior_path"],
            "artifact_sha256": case["prior_sha256"],
            "records": copy.deepcopy(prior["records"]),
            "qualification_review": copy.deepcopy(prior["qualification_review"]),
            "authority": prior["authority"],
        },
        "task_contract": {
            "surfaces": ["unresolved_matter", "reopen_condition"],
            "maximum_records_per_surface": 2,
            "valid_zero_output": True,
            "valid_ambiguous_output": True,
            "source_supported_inference_allowed": True,
            "external_fact_invention_allowed": False,
        },
        "boundary": {
            "authoritative_source_precedes_prior_interpretation_in_prompt": True,
            "semantic_meaning_decided_by_model": True,
            "prior_interpretations_may_be_incomplete": True,
            "deterministic_semantic_absence_inference": False,
            "keyword_or_chronology_gate": False,
            "quality_or_pressure_decision": False,
        },
    }
    return {**packet_body, "packet_sha256": value_sha256(packet_body)}, registry


def _request_preview(
    *,
    case_id: str,
    arm: str,
    prompts: dict[str, str],
    schema: dict[str, Any],
    schema_name: str,
) -> dict[str, Any]:
    body = {
        "max_tokens": 1600,
        "messages": [
            {"role": "system", "content": prompts["system_prompt"]},
            {"role": "user", "content": prompts["user_prompt"]},
        ],
        "model": "google/gemini-3.1-flash-lite",
        "provider": copy.deepcopy(PROVIDER),
        "reasoning": {"effort": "minimal", "exclude": True},
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": copy.deepcopy(schema),
            },
        },
        "seed": SEEDS[case_id],
        "stream": False,
    }
    return {
        "schema_version": "lolla.r4_matched_residual_request_preview.v1",
        "status": "provider_free_preview_not_authorized_for_transport",
        "case_id": case_id,
        "arm": arm,
        "body": body,
        "body_sha256": value_sha256(body),
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "authorization_present": False,
    }


def _json_difference_paths(left: Any, right: Any, path: str = "") -> list[str]:
    if type(left) is not type(right):
        return [path]
    if isinstance(left, dict):
        result: list[str] = []
        for key in sorted(set(left) | set(right)):
            child = f"{path}/{key}"
            if key not in left or key not in right:
                result.append(child)
            else:
                result.extend(_json_difference_paths(left[key], right[key], child))
        return result
    if isinstance(left, list):
        if len(left) != len(right):
            return [path]
        result = []
        for index, (left_value, right_value) in enumerate(zip(left, right)):
            result.extend(
                _json_difference_paths(left_value, right_value, f"{path}/{index}")
            )
        return result
    return [] if left == right else [path]


def _estimated_tokens(utf8_bytes: int) -> int:
    return (utf8_bytes + 1) // 2


def _component(name: str, raw: bytes) -> dict[str, Any]:
    return {
        "name": name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "utf8_bytes": len(raw),
        "estimated_tokens": _estimated_tokens(len(raw)),
    }


def _context_manifest(
    *,
    case: dict[str, Any],
    packet: dict[str, Any],
    preview: dict[str, Any],
    prompts: dict[str, str],
    schema: dict[str, Any],
) -> dict[str, Any]:
    body = preview["body"]
    user = prompts["user_prompt"]
    source_text = canonical_json_bytes(packet["source"]).decode("utf-8")
    prior_text = canonical_json_bytes(
        packet["prior_interpretation_context"]
    ).decode("utf-8")
    task_start = user.index("<task>\n") + len("<task>\n")
    task_end = user.index("\n</task>", task_start)
    task = user[task_start:task_end]
    source_raw = source_text.encode("utf-8")
    prior_raw = prior_text.encode("utf-8")
    system_raw = prompts["system_prompt"].encode("utf-8")
    task_raw = task.encode("utf-8")
    schema_raw = canonical_json_bytes(schema)
    message_bytes = sum(
        len(row["content"].encode("utf-8")) for row in body["messages"]
    )
    complete = (
        user.count(source_text) == 1
        and len(packet["source"]["aliases"])
        == len(case["source"]["messages"])
        and [row["text"] for row in packet["source"]["aliases"]]
        == [row["text"] for row in case["source"]["messages"]]
    )
    return {
        "schema_version": "lolla.r4_matched_residual_context_manifest.v1",
        "case_id": packet["case_id"],
        "arm": preview["arm"],
        "section_order": [
            "system_instruction",
            "authoritative_source",
            "fallible_prior_interpretation_context",
            "task",
        ],
        "context_components": [
            _component("system_instruction", system_raw),
            _component("authoritative_source", source_raw),
            _component("fallible_prior_interpretation_context", prior_raw),
            _component("task", task_raw),
            _component("schema", schema_raw),
        ],
        "source": {
            "artifact_path": case["source_path"],
            "artifact_sha256": case["source_sha256"],
            "artifact_utf8_bytes": len((ROOT / case["source_path"]).read_bytes()),
            "canonical_context_sha256": hashlib.sha256(source_raw).hexdigest(),
            "canonical_context_utf8_bytes": len(source_raw),
            "estimated_tokens": _estimated_tokens(len(source_raw)),
            "message_count": packet["source"]["message_count"],
            "alias_count": len(packet["source"]["aliases"]),
            "included_exactly_once": user.count(source_text) == 1,
            "summarized_or_chunked": False,
        },
        "prior": {
            "artifact_path": case["prior_path"],
            "artifact_sha256": case["prior_sha256"],
            "artifact_utf8_bytes": len((ROOT / case["prior_path"]).read_bytes()),
            "canonical_context_sha256": hashlib.sha256(prior_raw).hexdigest(),
            "canonical_context_utf8_bytes": len(prior_raw),
            "estimated_tokens": _estimated_tokens(len(prior_raw)),
            "record_count": len(packet["prior_interpretation_context"]["records"]),
            "included_exactly_once": user.count(prior_text) == 1,
            "summarized_or_reordered": False,
            "fallible_authority": packet["prior_interpretation_context"]["authority"],
        },
        "complete_source_inclusion": complete,
        "source_then_prior_order": user.index(source_text) < user.index(prior_text),
        "task_at_end_invariant": user.rstrip().endswith("</task>"),
        "fallible_prior_declaration": "fallible" in prompts["system_prompt"].lower(),
        "schema_labels_and_descriptions_are_model_context": True,
        "request_estimate": {
            "message_utf8_bytes": message_bytes,
            "schema_utf8_bytes": len(schema_raw),
            "total_context_utf8_bytes": message_bytes + len(schema_raw),
            "estimated_input_tokens": _estimated_tokens(message_bytes + len(schema_raw)),
            "estimator": "ceil((message_utf8_bytes+schema_utf8_bytes)/2); deterministic conservative estimate, not provider tokenization",
            "maximum_output_tokens": body["max_tokens"],
            "canonical_body_utf8_bytes": len(canonical_json_bytes(body)),
            "canonical_body_sha256": value_sha256(body),
        },
        "matched_equal_request_fields": [
            "/max_tokens",
            "/model",
            "/provider",
            "/reasoning",
            "/seed",
            "/stream",
        ],
        "changed_provider_visible_semantic_fields": [
            "system role",
            "task operation",
            "surface vocabulary",
            "schema name",
            "schema enum labels and semantic descriptions",
            "minimal examples",
            "evidence wording",
            "output rules",
        ],
        "unchanged_dimensions": [
            "authoritative source bytes and canonical context",
            "fallible prior bytes, records, and canonical context",
            "source then prior then task order",
            "paired two-surface task shape",
            "record fields and bounds",
            "model and pinned provider route",
            "seed within each matched pair",
            "1600-token output allocation",
            "minimal excluded-reasoning envelope",
            "nonstreaming strict-JSON policy",
            "privacy and routing controls",
            "relationship, graph, runtime, and operator",
        ],
        "no_summary_chunking_filter_or_semantic_gate": True,
        "declared_omissions": [
            "protected source-first target and target hash",
            "provider output and provider authorization",
            "relationship, evaluator, embedding, graph, pipeline, and runtime calls",
            "retries, semantic retries, fallbacks, healing, and model substitution",
            "summaries, chunks, relevance filters, and deterministic semantic gates",
            "governed-pending output surface and task split",
        ],
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }


def validate_matched_request_pair(
    *,
    packet: dict[str, Any],
    arm_a: dict[str, Any],
    arm_b: dict[str, Any],
) -> dict[str, Any]:
    """Rebuild both frozen arms and reject any undeclared request difference."""

    case_id = str(packet["case_id"])
    v2_schema = uncertainty_response_schema_v1()
    residual_schema = residual_response_schema_v1()
    expected_a = _request_preview(
        case_id=case_id,
        arm="A_frozen_v2_semantic_distinction",
        prompts=build_uncertainty_prompts_v2(packet),
        schema=v2_schema,
        schema_name="lolla_r4_uncertainty_v1",
    )
    expected_b = _request_preview(
        case_id=case_id,
        arm="B_frozen_residual_task",
        prompts=build_residual_prompts_v1(packet),
        schema=residual_schema,
        schema_name="lolla_r4_residual_task_v1",
    )
    if arm_a != expected_a:
        raise R4MatchedResidualHoldoutError(
            "arm A request does not equal the exact frozen v2 construction"
        )
    if arm_b != expected_b:
        raise R4MatchedResidualHoldoutError(
            "arm B request does not equal the exact frozen residual construction"
        )
    allowed_schema_differences = [
        "/description",
        "/properties/reviews/description",
        "/properties/reviews/items/description",
        "/properties/reviews/items/properties/outcome/description",
        "/properties/reviews/items/properties/records/description",
        "/properties/reviews/items/properties/records/items/description",
        "/properties/reviews/items/properties/records/items/properties/evidence_ids/description",
        "/properties/reviews/items/properties/records/items/properties/interpretation/description",
        "/properties/reviews/items/properties/records/items/properties/limitations/description",
        "/properties/reviews/items/properties/records/items/properties/support/description",
        "/properties/reviews/items/properties/surface/description",
        "/properties/reviews/items/properties/surface/enum/0",
        "/properties/reviews/items/properties/surface/enum/1",
    ]
    schema_differences = _json_difference_paths(v2_schema, residual_schema)
    undeclared = sorted(set(schema_differences) - set(allowed_schema_differences))
    equal_fields = [
        f"/{field}"
        for field in (
            "max_tokens",
            "model",
            "provider",
            "reasoning",
            "seed",
            "stream",
        )
        if arm_a["body"][field] == arm_b["body"][field]
    ]
    if len(equal_fields) != 6 or undeclared:
        raise R4MatchedResidualHoldoutError("undeclared matched request delta")
    source_text = canonical_json_bytes(packet["source"]).decode("utf-8")
    prior_text = canonical_json_bytes(
        packet["prior_interpretation_context"]
    ).decode("utf-8")
    users = [
        arm_a["body"]["messages"][1]["content"],
        arm_b["body"]["messages"][1]["content"],
    ]
    matched_context = all(
        user.count(source_text) == 1
        and user.count(prior_text) == 1
        and user.index(source_text) < user.index(prior_text) < user.index("<task>")
        for user in users
    )
    if not matched_context:
        raise R4MatchedResidualHoldoutError("undeclared matched request delta")
    return {
        "schema_version": "lolla.r4_matched_request_delta.v1",
        "case_id": case_id,
        "matched_source_and_prior": True,
        "equal_body_fields": equal_fields,
        "allowed_provider_visible_change_categories": [
            "role",
            "task operation",
            "surface vocabulary",
            "schema name and enum descriptions",
            "examples",
            "evidence wording",
            "output rules",
        ],
        "changed_body_paths": [
            "/messages/0/content",
            "/messages/1/content/task_operation_and_vocabulary_only",
            "/response_format/json_schema/name",
            "/response_format/json_schema/schema/declared_semantic_labels_and_descriptions_only",
        ],
        "schema_difference_paths": schema_differences,
        "undeclared_differences": [],
        "paired_task_shape_unchanged": True,
    }


def build_files(output: Path = DEFAULT_OUTPUT) -> dict[str, bytes]:
    """Build exact matched previews in memory without provider transport."""

    load_source_first_targets()
    inputs = load_frozen_case_inputs()
    files: dict[str, bytes] = {}
    v2_schema = uncertainty_response_schema_v1()
    residual_schema = residual_response_schema_v1()
    case_records: dict[str, dict[str, Any]] = {}
    for case_id in CASE_IDS:
        packet, registry = _packet(inputs[case_id])
        prompts_a = build_uncertainty_prompts_v2(packet)
        prompts_b = build_residual_prompts_v1(packet)
        arm_a = _request_preview(
            case_id=case_id,
            arm="A_frozen_v2_semantic_distinction",
            prompts=prompts_a,
            schema=v2_schema,
            schema_name="lolla_r4_uncertainty_v1",
        )
        arm_b = _request_preview(
            case_id=case_id,
            arm="B_frozen_residual_task",
            prompts=prompts_b,
            schema=residual_schema,
            schema_name="lolla_r4_residual_task_v1",
        )
        delta = validate_matched_request_pair(
            packet=packet, arm_a=arm_a, arm_b=arm_b
        )
        case_root = output / "cases" / case_id
        manifest_a = _context_manifest(
            case=inputs[case_id],
            packet=packet,
            preview=arm_a,
            prompts=prompts_a,
            schema=v2_schema,
        )
        manifest_b = _context_manifest(
            case=inputs[case_id],
            packet=packet,
            preview=arm_b,
            prompts=prompts_b,
            schema=residual_schema,
        )
        values = {
            "source-registry.json": registry,
            "uncertainty-packet.json": packet,
            "arm-a-prompts.json": prompts_a,
            "arm-a-request-preview.json": arm_a,
            "arm-b-prompts.json": prompts_b,
            "arm-b-request-preview.json": arm_b,
            "arm-a-context-manifest.json": manifest_a,
            "arm-b-context-manifest.json": manifest_b,
            "matched-request-delta.json": delta,
        }
        for name, value in values.items():
            files[_relative(case_root / name)] = _render(value)
        arm_records = {}
        for key, label, preview, manifest in (
            ("A", "A_frozen_v2_semantic_distinction", arm_a, manifest_a),
            ("B", "B_frozen_residual_task", arm_b, manifest_b),
        ):
            estimated_input = manifest["request_estimate"]["estimated_input_tokens"]
            estimated_cost = round(
                estimated_input * 0.25 / 1_000_000
                + 1600 * 1.5 / 1_000_000,
                9,
            )
            arm_records[key] = {
                "arm": label,
                "request_preview_path": _relative(
                    case_root / f"arm-{key.lower()}-request-preview.json"
                ),
                "request_body_sha256": preview["body_sha256"],
                "context_manifest_path": _relative(
                    case_root / f"arm-{key.lower()}-context-manifest.json"
                ),
                "estimated_input_tokens": estimated_input,
                "maximum_output_tokens": 1600,
                "conservative_estimated_cost_usd": estimated_cost,
            }
        case_records[case_id] = {
            "case_id": case_id,
            "source_path": inputs[case_id]["source_path"],
            "source_sha256": inputs[case_id]["source_sha256"],
            "prior_path": inputs[case_id]["prior_path"],
            "prior_sha256": inputs[case_id]["prior_sha256"],
            "packet_path": _relative(case_root / "uncertainty-packet.json"),
            "packet_sha256": hashlib.sha256(
                files[_relative(case_root / "uncertainty-packet.json")]
            ).hexdigest(),
            "source_registry_path": _relative(case_root / "source-registry.json"),
            "matched_request_delta_path": _relative(
                case_root / "matched-request-delta.json"
            ),
            "arms": arm_records,
            "matched_case_cost_usd": round(
                sum(row["conservative_estimated_cost_usd"] for row in arm_records.values()),
                9,
            ),
        }

    order = (
        (CASE_IDS[0], "A"),
        (CASE_IDS[0], "B"),
        (CASE_IDS[1], "B"),
        (CASE_IDS[1], "A"),
        (CASE_IDS[2], "B"),
        (CASE_IDS[2], "A"),
        (CASE_IDS[3], "A"),
        (CASE_IDS[3], "B"),
    )
    call_plan = []
    for ordinal, (case_id, arm_key) in enumerate(order, 1):
        arm = case_records[case_id]["arms"][arm_key]
        call_plan.append(
            {
                "ordinal": ordinal,
                "case_id": case_id,
                "arm": arm["arm"],
                "request_preview_path": arm["request_preview_path"],
                "request_body_sha256": arm["request_body_sha256"],
                "conservative_estimated_cost_usd": arm[
                    "conservative_estimated_cost_usd"
                ],
            }
        )
    total_estimate = round(
        sum(row["conservative_estimated_cost_usd"] for row in call_plan), 9
    )
    frozen_history = {
        "v1_module_sha256": _file_sha(
            ROOT / "engine/system_b/r4_complementary_readers.py"
        ),
        "v2_module_sha256": _file_sha(
            ROOT / "engine/system_b/r4_semantic_distinction.py"
        ),
        "residual_module_sha256": _file_sha(
            ROOT / "engine/system_b/r4_residual_task.py"
        ),
        "v2_schema_sha256": value_sha256(v2_schema),
        "residual_schema_sha256": value_sha256(residual_schema),
        "provider_free_corpus_replay": {
            "cases": 12,
            "case_artifact_links": 543,
            "unique_frozen_json_artifacts": 400,
        },
    }
    expected_history = {
        "v1_module_sha256": "9253290093e62f62a9adbf8902ccf010ac4d4417c345222e4756e771496bf777",
        "v2_module_sha256": "e774b19cd2bac461e6d586dffbde48515ab23d6f73e1eb158ed87bdcdccdf3c8",
        "residual_module_sha256": "726d4bc649e8e488b5783906785fc3b481ba3ce295dac5155fcff8cd0a83616a",
        "v2_schema_sha256": "12327510a78c24bcc1b89e874112517288e1a2054159def729da094de1404a65",
        "residual_schema_sha256": "70e62d8faa27fcff6517ebaf54433ecd8f534690d86cfc6d219a1e8420b42087",
        "provider_free_corpus_replay": {
            "cases": 12,
            "case_artifact_links": 543,
            "unique_frozen_json_artifacts": 400,
        },
    }
    if frozen_history != expected_history:
        raise R4MatchedResidualHoldoutError("historical v1/v2/residual boundary drifted")

    runner_files = {
        path: raw
        for path, raw in files.items()
        if path.endswith(
            (
                "source-registry.json",
                "uncertainty-packet.json",
                "request-preview.json",
                "context-manifest.json",
                "matched-request-delta.json",
            )
        )
    }
    execution_manifest = {
        "schema_version": "lolla.r4_matched_residual_execution_manifest.v1",
        "status": "frozen_runner_visible_inputs_no_authorization",
        "files": [
            {"path": path, "sha256": hashlib.sha256(raw).hexdigest(), "utf8_bytes": len(raw)}
            for path, raw in sorted(runner_files.items())
        ],
        "protected_review_reference_present": False,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }
    execution_manifest_path = _relative(output / "execution-manifest.json")
    files[execution_manifest_path] = _render(execution_manifest)

    contract = {
        "schema_version": "lolla.r4_matched_residual_holdout_contract.v1",
        "status": "provider_free_matched_holdout_frozen_no_authorization",
        "date": "2026-07-14",
        "run_id": "lolla-r4-matched-residual-holdout-v1",
        "falsifiable_question": "On the same genuinely new hidden long-form evidence, does the residual-task contract improve false-positive restraint over frozen v2 while preserving sensitivity to materially distinct residuals?",
        "cases": [case_records[case_id] for case_id in CASE_IDS],
        "call_plan": call_plan,
        "counterbalancing": {
            "fixed_before_execution": True,
            "arm_a_first_cases": [CASE_IDS[0], CASE_IDS[3]],
            "arm_b_first_cases": [CASE_IDS[1], CASE_IDS[2]],
            "same_seed_within_each_case": True,
        },
        "operator": {
            "endpoint": "https://openrouter.ai/api/v1/chat/completions",
            "model": "google/gemini-3.1-flash-lite",
            "allowed_served_model_ids": [
                "google/gemini-3.1-flash-lite",
                "google/gemini-3.1-flash-lite-20260507",
            ],
            "provider_slug": "google-vertex",
            "allowed_served_provider_names": ["Google"],
            "provider_order": ["google-vertex"],
            "provider_only": ["google-vertex"],
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "deny",
            "zdr": True,
            "maximum_price_usd_per_million_tokens": {
                "prompt": 0.25,
                "completion": 1.5,
            },
            "seed_policy": "one fixed seed per case, byte-identical between arms",
            "maximum_output_tokens": 1600,
            "reasoning": {"effort": "minimal", "exclude": True},
            "stream": False,
            "strict_json_schema": True,
        },
        "budget": {
            "maximum_provider_calls": 8,
            "hard_provider_reported_cost_per_case_usd": 0.015,
            "hard_provider_reported_cost_total_usd": 0.06,
            "conservative_estimated_total_cost_usd": total_estimate,
            "automatic_retries": 0,
            "semantic_retries": 0,
            "fallback_models": 0,
            "response_healing": False,
            "relationship_calls": 0,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "pipeline_calls": 0,
            "runtime_calls": 0,
        },
        "execution_envelope": {
            "first_terminal_provider_result_preserved_exactly": True,
            "stop_on_transport_failure": True,
            "stop_on_provider_identity_failure": True,
            "stop_on_budget_failure": True,
            "stop_on_schema_or_local_admission_failure": True,
            "stop_on_reasoning_custody_failure": True,
            "stop_on_authorization_failure": True,
            "generation_identity_required": True,
            "exact_usage_and_provider_reported_cost_required": True,
            "request_and_raw_response_hashes_required": True,
            "no_retry_fallback_healing_or_substitution": True,
            "no_relationship_evaluator_embedding_graph_pipeline_or_runtime_calls": True,
            "execution_manifest_path": execution_manifest_path,
            "execution_manifest_sha256": hashlib.sha256(
                files[execution_manifest_path]
            ).hexdigest(),
            "target_access_possible": False,
        },
        "evaluation_contract": {
            "vector": [
                "mechanical_execution_and_exact_provider_attribution",
                "false_positive_restraint",
                "genuine_residual_sensitivity",
                "zero_versus_ambiguity_behavior",
                "evidence_precision",
                "semantic_surface_placement",
                "speaker_and_modal_fidelity",
                "prior_anchoring_resistance",
                "long_context_and_late_evidence_use",
                "operational_cost_and_custody",
            ],
            "scalar_quality_score": None,
            "mixed_findings_must_not_be_collapsed": True,
        },
        "decision_matrix": {
            "residual_task_identity_supported": "Residual passes all restraint and sensitivity gates while v2 repeats predicted broad-inventory errors.",
            "holdout_non_discriminating": "Both arms pass.",
            "residual_task_overcorrected": "Residual quiets controls but misses either genuine residual.",
            "residual_task_repair_insufficient": "Residual repeats safeguard, fallback, or review false positives.",
            "residual_task_regressed": "Residual performs materially worse than v2.",
            "semantic_result_not_evaluable": "Mechanical or custody failure prevents matched comparison.",
        },
        "current_official_practice": {
            "path": _relative(PRACTICE),
            "sha256": _file_sha(PRACTICE),
            "date_checked": "2026-07-14",
            "primary_sources_only": True,
        },
        "future_runner": {
            "path": _relative(RUNNER),
            "sha256": _file_sha(RUNNER),
            "network_transport_created_only_after_authorization": True,
            "dry_run_provider_calls": 0,
        },
        "frozen_history": frozen_history,
        "decision_boundary": {
            "provider_calls_authorized": False,
            "authorization_file_present": False,
            "package_grants_authorization": False,
            "package_requests_authorization": False,
            "holdout_execution_authorized": False,
            "relationship_validation_authorized": False,
            "runtime_or_graph_integration_authorized": False,
            "model_comparison_authorized": False,
            "r5_authorized": False,
            "product_usefulness_claim_authorized": False,
        },
        "provider_calls_made": 0,
        "provider_cost_usd": 0.0,
        "non_claims": [
            "This design does not authorize or request a provider call.",
            "Provider-free contract and fixture validity are not model semantic validation.",
            "The four cases are simulated reliability evidence, not real-user evidence.",
            "A future matched result does not establish product usefulness or authorize integration.",
        ],
    }
    files[CONTRACT_RELATIVE] = _render(contract)

    review_manifest = {
        "schema_version": "lolla.r4_matched_residual_review_evidence_manifest.v1",
        "status": "protected_source_first_review_evidence_frozen_separately",
        "protected_target": {
            "path": _relative(TARGET),
            "sha256": _file_sha(TARGET),
        },
        "source_prior_freeze_manifest": {
            "path": _relative(INPUT_ROOT / "freeze-manifest.json"),
            "sha256": _file_sha(INPUT_ROOT / "freeze-manifest.json"),
        },
        "runner_may_load_this_manifest": False,
        "provider_visible": False,
        "provider_outputs_existed_when_target_was_authored": False,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }
    files[_relative(output / "review-evidence-manifest.json")] = _render(
        review_manifest
    )
    artifact_manifest = {
        "schema_version": "lolla.r4_matched_residual_artifact_manifest.v1",
        "status": "provider_free_exact_holdout_design_artifacts_frozen",
        "date": "2026-07-14",
        "files": [
            {"path": path, "sha256": hashlib.sha256(raw).hexdigest(), "utf8_bytes": len(raw)}
            for path, raw in sorted(files.items())
        ],
        "file_count": len(files),
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }
    files[_relative(output / "manifest.json")] = _render(artifact_manifest)
    return files


def _validate_files(files: dict[str, bytes]) -> dict[str, Any]:
    for relative, expected in files.items():
        path = ROOT / relative
        if not path.is_file() or path.read_bytes() != expected:
            raise R4MatchedResidualHoldoutError(
                f"matched holdout artifact drifted: {relative}"
            )
    contract = _load(ROOT / CONTRACT_RELATIVE)
    if (
        contract.get("status")
        != "provider_free_matched_holdout_frozen_no_authorization"
        or contract.get("provider_calls_made") != 0
        or contract.get("provider_cost_usd") != 0.0
        or contract.get("decision_boundary", {}).get("provider_calls_authorized")
        is not False
    ):
        raise R4MatchedResidualHoldoutError("matched holdout decision boundary drifted")
    return contract


def build(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    files = build_files(output)
    for relative, raw in files.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return _validate_files(files)


def validate(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    return _validate_files(build_files(output))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    result = validate(args.output.resolve()) if args.validate_only else build(
        args.output.resolve()
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "provider_calls_made": result["provider_calls_made"],
                "provider_cost_usd": result["provider_cost_usd"],
                "provider_calls_authorized": result["decision_boundary"][
                    "provider_calls_authorized"
                ],
                "conservative_estimated_total_cost_usd": result["budget"][
                    "conservative_estimated_total_cost_usd"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
