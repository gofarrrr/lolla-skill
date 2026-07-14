#!/usr/bin/env python3
"""Build the provider-free R4 paired-versus-separated task-shape package."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.conversation_state_fan_in import build_source_registry
from engine.system_b.r4_complementary_readers import (
    UNCERTAINTY_PACKET_SCHEMA,
    canonical_json_bytes,
    value_sha256,
)
from engine.system_b.r4_residual_task import (
    RESIDUAL_PROVIDER_SURFACES,
    build_residual_prompts_v1,
    residual_response_schema_v1,
)


ROOT = Path(__file__).resolve().parents[2]
FREEZE_ROOT = ROOT / "research/lolla-r4-separated-surface-experiment-v1-source-freeze-2026-07-14"
OUTPUT_ROOT = ROOT / "research/lolla-r4-separated-surface-experiment-v1-contract-2026-07-14"
CONTRACT_PATH = ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-contract.json"
RUNNER_PATH = ROOT / "scripts/evals/run_r4_separated_surface_experiment.py"
TARGET_PATH = ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-target.json"
TARGET_REVIEW_PATH = ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-target-review.json"
TARGET_CHECKPOINT = "740a5257c725f8eca5f51dde2c27b01437ad2fdb"
CASE_IDS = (
    "r4s1-case01-cave-rescue-readiness",
    "r4s1-case02-neighborhood-observatory-winter-access",
    "r4s1-case03-relaxed-performance-tour",
    "r4s1-case04-native-seed-cryopreservation",
)
SEEDS = {
    CASE_IDS[0]: 74101,
    CASE_IDS[1]: 74102,
    CASE_IDS[2]: 74103,
    CASE_IDS[3]: 74104,
}
PROVIDER = {
    "order": ["google-vertex"],
    "only": ["google-vertex"],
    "allow_fallbacks": False,
    "require_parameters": True,
    "data_collection": "deny",
    "zdr": True,
    "max_price": {"prompt": 0.25, "completion": 1.5},
}
OPERATOR = {
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
    "maximum_price_usd_per_million_tokens": {"prompt": 0.25, "completion": 1.5},
    "reasoning": {"effort": "minimal", "exclude": True},
    "stream": False,
    "strict_json_schema": True,
}


class R4SeparatedSurfaceBuildError(RuntimeError):
    """Raised when the frozen design or its deterministic custody drifts."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4SeparatedSurfaceBuildError(f"expected JSON object: {path}")
    return value


def _render(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _estimated_tokens(raw: bytes) -> int:
    return (len(raw) + 1) // 2


def _file_record(path: Path, raw: bytes | None = None) -> dict[str, Any]:
    payload = path.read_bytes() if raw is None else raw
    return {"path": _relative(path), "sha256": _sha_bytes(payload), "utf8_bytes": len(payload)}


def _assert_checkpoint_order() -> None:
    if subprocess.run(["git", "merge-base", "--is-ancestor", TARGET_CHECKPOINT, "HEAD"], cwd=ROOT, check=False).returncode != 0:
        raise R4SeparatedSurfaceBuildError("protected target checkpoint is not an ancestor")
    for path in (TARGET_PATH, TARGET_REVIEW_PATH):
        result = subprocess.run(["git", "cat-file", "-e", f"{TARGET_CHECKPOINT}:{_relative(path)}"], cwd=ROOT, check=False, capture_output=True)
        if result.returncode != 0:
            raise R4SeparatedSurfaceBuildError("protected target is not frozen at checkpoint")
    if _load(TARGET_REVIEW_PATH).get("request_previews_existed_when_target_frozen") is not False:
        raise R4SeparatedSurfaceBuildError("target freeze order drifted")


def _load_cases() -> dict[str, dict[str, Any]]:
    manifest = _load(FREEZE_ROOT / "freeze-manifest.json")
    if _sha(FREEZE_ROOT / "freeze-manifest.json") != "ee39536238421efb7d8c6b28a0c6acfcbf10d6f4cfc8064f8f6ad5bbd3919921":
        raise R4SeparatedSurfaceBuildError("source freeze manifest drifted")
    cases: dict[str, dict[str, Any]] = {}
    for row in manifest["cases"]:
        case_id = row["case_id"]
        source_path = ROOT / row["source"]["path"]
        prior_path = ROOT / row["prior"]["path"]
        if _sha(source_path) != row["source"]["sha256"] or _sha(prior_path) != row["prior"]["sha256"]:
            raise R4SeparatedSurfaceBuildError(f"reviewed bytes drifted: {case_id}")
        cases[case_id] = {
            "case_id": case_id,
            "source": _load(source_path),
            "prior": _load(prior_path),
            "source_path": _relative(source_path),
            "prior_path": _relative(prior_path),
            "source_sha256": row["source"]["sha256"],
            "prior_sha256": row["prior"]["sha256"],
        }
    if tuple(cases) != CASE_IDS:
        raise R4SeparatedSurfaceBuildError("case portfolio drifted")
    return cases


def _packet(case: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    aliases: list[dict[str, Any]] = []
    registry_aliases: list[dict[str, Any]] = []
    for row in case["source"]["messages"]:
        index = int(row["message_index"])
        alias = row["alias"]
        text = str(row["text"])
        text_sha = _sha_bytes(text.encode("utf-8"))
        aliases.append({"alias": alias, "speaker": row["speaker"], "text": text, "text_sha256": text_sha, "turn_index": (index + 1) // 2})
        registry_aliases.append({"alias": alias, "span_id": f"span-{case['case_id']}-{index:03d}", "speaker": row["speaker"], "text_sha256": text_sha, "turn_index": (index + 1) // 2})
    source_path = case["source_path"]
    registry = build_source_registry(
        case_id=case["case_id"], source_path=source_path,
        source_bytes=(ROOT / source_path).read_bytes(), message_count=28,
        aliases=registry_aliases,
    )
    body = {
        "schema_version": UNCERTAINTY_PACKET_SCHEMA,
        "status": "provider_free_separated_surface_input_frozen",
        "case_id": case["case_id"],
        "source": {"path": source_path, "sha256": case["source_sha256"], "message_count": 28, "aliases": aliases},
        "prior_interpretation_context": {
            "artifact_path": case["prior_path"], "artifact_sha256": case["prior_sha256"],
            "records": copy.deepcopy(case["prior"]["records"]),
            "qualification_review": copy.deepcopy(case["prior"]["qualification_review"]),
            "authority": case["prior"]["authority"],
        },
        "task_contract": {
            "surfaces": ["unresolved_matter", "reopen_condition"],
            "maximum_records_per_surface": 2, "valid_zero_output": True,
            "valid_ambiguous_output": True, "source_supported_inference_allowed": True,
            "external_fact_invention_allowed": False,
        },
        "boundary": {
            "authoritative_source_precedes_prior_interpretation_in_prompt": True,
            "semantic_meaning_decided_by_model": True,
            "prior_interpretations_may_be_incomplete": True,
            "deterministic_semantic_absence_inference": False,
            "keyword_or_chronology_gate": False, "quality_or_pressure_decision": False,
        },
    }
    return {**body, "packet_sha256": value_sha256(body)}, registry


def _single_schema(surface: str) -> dict[str, Any]:
    schema = copy.deepcopy(residual_response_schema_v1())
    schema["description"] = f"Single residual-discovery review for {surface}."
    reviews = schema["properties"]["reviews"]
    reviews["description"] = f"Exactly one review for {surface}."
    reviews["minItems"] = 1
    reviews["maxItems"] = 1
    reviews["items"]["properties"]["surface"]["enum"] = [surface]
    return schema


def _single_prompts(packet: Mapping[str, Any], surface: str) -> dict[str, str]:
    paired = build_residual_prompts_v1(packet)
    prefix = paired["user_prompt"].split("<task>\n", 1)[0]
    user = (
        prefix + "<task>\nPerform residual accounting and subtraction over the complete source. "
        f"Return exactly one review for {surface}, with at most two records. "
        "Preserve exact aliases, speaker ownership, and modal force. Do not give advice, select a graph, or score quality.\n</task>"
    )
    return {
        "prompt_contract_version": "lolla.r4_residual_task_prompt.v1_single_surface_shape",
        "system_prompt": paired["system_prompt"], "user_prompt": user,
        "system_prompt_sha256": _sha_bytes(paired["system_prompt"].encode("utf-8")),
        "user_prompt_sha256": _sha_bytes(user.encode("utf-8")),
    }


def _preview(case: Mapping[str, Any], packet: Mapping[str, Any], *, arm: str, surface: str | None, prompts: Mapping[str, str], schema: Mapping[str, Any]) -> dict[str, Any]:
    paired = surface is None
    requested = list(RESIDUAL_PROVIDER_SURFACES) if paired else [surface]
    body = {
        "max_tokens": 1600 if paired else 800,
        "messages": [{"role": "system", "content": prompts["system_prompt"]}, {"role": "user", "content": prompts["user_prompt"]}],
        "model": OPERATOR["model"], "provider": copy.deepcopy(PROVIDER),
        "reasoning": copy.deepcopy(OPERATOR["reasoning"]),
        "response_format": {"type": "json_schema", "json_schema": {"name": "lolla_r4_residual_paired_v1" if paired else f"lolla_r4_{surface}_single_v1", "strict": True, "schema": copy.deepcopy(schema)}},
        "seed": SEEDS[case["case_id"]], "stream": False,
    }
    source_text = canonical_json_bytes(packet["source"]).decode("utf-8")
    prior_text = canonical_json_bytes(packet["prior_interpretation_context"]).decode("utf-8")
    user = prompts["user_prompt"]
    return {
        "schema_version": "lolla.r4_separated_surface_request_preview.v1",
        "status": "provider_free_preview_not_authorized_for_transport",
        "case_id": case["case_id"], "arm": arm,
        "requested_provider_surfaces": requested,
        "source_sha256": case["source_sha256"], "prior_sha256": case["prior_sha256"],
        "source_aliases": [row["alias"] for row in packet["source"]["aliases"]],
        "complete_source_included_once": user.count(source_text) == 1,
        "complete_prior_included_once": user.count(prior_text) == 1,
        "source_then_prior_then_task": user.index(source_text) < user.index(prior_text) < user.index("<task>"),
        "task_at_end": user.rstrip().endswith("</task>"),
        "body": body, "body_sha256": value_sha256(body),
        "provider_calls": 0, "provider_cost_usd": 0.0, "authorization_present": False,
    }


def _component(name: str, raw: bytes) -> dict[str, Any]:
    return {"name": name, "sha256": _sha_bytes(raw), "utf8_bytes": len(raw), "estimated_tokens": _estimated_tokens(raw)}


def _context_manifest(case: Mapping[str, Any], packet: Mapping[str, Any], preview: Mapping[str, Any], prompts: Mapping[str, str], schema: Mapping[str, Any]) -> dict[str, Any]:
    source_raw = canonical_json_bytes(packet["source"])
    prior_raw = canonical_json_bytes(packet["prior_interpretation_context"])
    system_raw = prompts["system_prompt"].encode("utf-8")
    task = prompts["user_prompt"].split("<task>\n", 1)[1].rsplit("\n</task>", 1)[0]
    task_raw = task.encode("utf-8")
    schema_raw = canonical_json_bytes(schema)
    message_bytes = sum(len(row["content"].encode("utf-8")) for row in preview["body"]["messages"])
    total = message_bytes + len(schema_raw)
    return {
        "schema_version": "lolla.r4_separated_surface_context_manifest.v1",
        "case_id": case["case_id"], "arm": preview["arm"],
        "section_order": ["system_instruction", "authoritative_source", "fallible_prior_interpretation_context", "task", "schema"],
        "context_components": [_component("system_instruction", system_raw), _component("authoritative_source", source_raw), _component("fallible_prior_interpretation_context", prior_raw), _component("task", task_raw), _component("schema", schema_raw)],
        "source": {"artifact_path": case["source_path"], "artifact_sha256": case["source_sha256"], "canonical_context_sha256": _sha_bytes(source_raw), "canonical_context_utf8_bytes": len(source_raw), "included_exactly_once": preview["complete_source_included_once"], "summarized_or_chunked": False},
        "prior": {"artifact_path": case["prior_path"], "artifact_sha256": case["prior_sha256"], "canonical_context_sha256": _sha_bytes(prior_raw), "canonical_context_utf8_bytes": len(prior_raw), "included_exactly_once": preview["complete_prior_included_once"], "summarized_or_reordered": False, "authority": packet["prior_interpretation_context"]["authority"]},
        "task_at_end": preview["task_at_end"], "complete_source_inclusion": preview["complete_source_included_once"],
        "source_then_prior_then_task": preview["source_then_prior_then_task"],
        "schema_is_provider_context": True,
        "request_estimate": {"message_utf8_bytes": message_bytes, "schema_utf8_bytes": len(schema_raw), "total_context_utf8_bytes": total, "estimated_input_tokens": _estimated_tokens(b"x" * total), "maximum_output_tokens": preview["body"]["max_tokens"], "canonical_body_utf8_bytes": len(canonical_json_bytes(preview["body"])), "canonical_body_sha256": preview["body_sha256"], "estimator": "ceil(utf8_bytes/2); conservative deterministic estimate, not provider tokenization"},
        "no_summary_chunking_filter_or_semantic_gate": True,
        "declared_omissions": ["protected evaluation evidence", "provider output", "execution authorization", "relationship, evaluator, embedding, graph, pipeline, and runtime calls"],
        "provider_calls": 0, "provider_cost_usd": 0.0,
    }


def _difference_paths(left: Any, right: Any, path: str = "") -> list[str]:
    if type(left) is not type(right):
        return [path or "/"]
    if isinstance(left, dict):
        result: list[str] = []
        for key in sorted(set(left) | set(right)):
            child = f"{path}/{key}"
            if key not in left or key not in right:
                result.append(child)
            else:
                result.extend(_difference_paths(left[key], right[key], child))
        return result
    if isinstance(left, list):
        if len(left) != len(right):
            return [path]
        result = []
        for index, pair in enumerate(zip(left, right)):
            result.extend(_difference_paths(pair[0], pair[1], f"{path}/{index}"))
        return result
    return [] if left == right else [path]


ALLOWED_DELTA_PREFIXES = [
    "/max_tokens",
    "/messages/1/content",
    "/response_format/json_schema/name",
    "/response_format/json_schema/schema/description",
    "/response_format/json_schema/schema/properties/reviews/description",
    "/response_format/json_schema/schema/properties/reviews/minItems",
    "/response_format/json_schema/schema/properties/reviews/maxItems",
    "/response_format/json_schema/schema/properties/reviews/items/properties/surface/enum",
]


def _delta_manifest(case_id: str, paired: Mapping[str, Any], separated: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    comparisons = []
    all_paths: list[str] = []
    undeclared: list[str] = []
    for row in separated:
        paths = _difference_paths(paired["body"], row["body"])
        all_paths.extend(paths)
        bad = [path for path in paths if not any(path.startswith(prefix) for prefix in ALLOWED_DELTA_PREFIXES)]
        undeclared.extend(bad)
        comparisons.append({"paired_arm": paired["arm"], "separated_arm": row["arm"], "exact_delta_paths": paths, "undeclared_delta_paths": bad})
    return {
        "schema_version": "lolla.r4_separated_surface_matched_delta.v1", "case_id": case_id,
        "comparisons": comparisons, "all_exact_delta_paths": sorted(set(all_paths)),
        "allowed_path_prefixes": ALLOWED_DELTA_PREFIXES,
        "undeclared_provider_visible_deltas": sorted(set(undeclared)),
        "semantic_wording_change": False, "source_or_prior_change": False,
        "inherent_input_duplication_declared": True,
        "provider_calls": 0, "provider_cost_usd": 0.0,
    }


def _build_support_files() -> tuple[dict[str, bytes], list[dict[str, Any]], list[dict[str, Any]]]:
    _assert_checkpoint_order()
    cases = _load_cases()
    paired_schema = residual_response_schema_v1()
    decision_schema = _single_schema(RESIDUAL_PROVIDER_SURFACES[0])
    dependency_schema = _single_schema(RESIDUAL_PROVIDER_SURFACES[1])
    files: dict[str, bytes] = {
        _relative(OUTPUT_ROOT / "paired-response-schema.json"): _render(paired_schema),
        _relative(OUTPUT_ROOT / "separated-decision-gap-response-schema.json"): _render(decision_schema),
        _relative(OUTPUT_ROOT / "separated-reconsideration-dependency-response-schema.json"): _render(dependency_schema),
    }
    contract_cases: list[dict[str, Any]] = []
    call_lookup: list[dict[str, Any]] = []
    for case_id in CASE_IDS:
        case = cases[case_id]
        packet, registry = _packet(case)
        prompts_p = build_residual_prompts_v1(packet)
        prompts_d = _single_prompts(packet, RESIDUAL_PROVIDER_SURFACES[0])
        prompts_r = _single_prompts(packet, RESIDUAL_PROVIDER_SURFACES[1])
        previews = [
            _preview(case, packet, arm="paired_residual", surface=None, prompts=prompts_p, schema=paired_schema),
            _preview(case, packet, arm="separated_decision_gap", surface=RESIDUAL_PROVIDER_SURFACES[0], prompts=prompts_d, schema=decision_schema),
            _preview(case, packet, arm="separated_reconsideration_dependency", surface=RESIDUAL_PROVIDER_SURFACES[1], prompts=prompts_r, schema=dependency_schema),
        ]
        prompts = [prompts_p, prompts_d, prompts_r]
        schemas = [paired_schema, decision_schema, dependency_schema]
        names = ["paired", "separated-decision-gap", "separated-reconsideration-dependency"]
        case_root = OUTPUT_ROOT / "cases" / case_id
        files[_relative(case_root / "uncertainty-packet.json")] = _render(packet)
        files[_relative(case_root / "source-registry.json")] = _render(registry)
        preview_paths: list[str] = []
        context_paths: list[str] = []
        for name, preview, prompt, schema in zip(names, previews, prompts, schemas):
            prompt_path = case_root / f"{name}-prompts.json"
            preview_path = case_root / f"{name}-request-preview.json"
            context_path = case_root / f"{name}-context-manifest.json"
            files[_relative(prompt_path)] = _render(prompt)
            files[_relative(preview_path)] = _render(preview)
            files[_relative(context_path)] = _render(_context_manifest(case, packet, preview, prompt, schema))
            preview_paths.append(_relative(preview_path))
            context_paths.append(_relative(context_path))
            call_lookup.append({
                "case_id": case_id, "arm": preview["arm"],
                "requested_surface": "both" if len(preview["requested_provider_surfaces"]) == 2 else preview["requested_provider_surfaces"][0],
                "request_preview_path": _relative(preview_path),
                "request_body_sha256": preview["body_sha256"],
                "maximum_output_tokens": preview["body"]["max_tokens"],
                "estimated_input_tokens": _context_manifest(case, packet, preview, prompt, schema)["request_estimate"]["estimated_input_tokens"],
            })
        delta = _delta_manifest(case_id, previews[0], previews[1:])
        if delta["undeclared_provider_visible_deltas"]:
            raise R4SeparatedSurfaceBuildError(f"undeclared request delta: {case_id}")
        delta_path = case_root / "matched-delta-manifest.json"
        files[_relative(delta_path)] = _render(delta)
        contract_cases.append({
            "case_id": case_id, "seed": SEEDS[case_id],
            "source_path": case["source_path"], "source_sha256": case["source_sha256"],
            "prior_path": case["prior_path"], "prior_sha256": case["prior_sha256"],
            "packet_path": _relative(case_root / "uncertainty-packet.json"),
            "source_registry_path": _relative(case_root / "source-registry.json"),
            "request_preview_paths": preview_paths, "context_manifest_paths": context_paths,
            "matched_delta_manifest_path": _relative(delta_path),
        })
    return files, contract_cases, call_lookup


ORDER = [
    (CASE_IDS[0], "paired_residual"), (CASE_IDS[0], "separated_decision_gap"), (CASE_IDS[0], "separated_reconsideration_dependency"),
    (CASE_IDS[1], "separated_decision_gap"), (CASE_IDS[1], "separated_reconsideration_dependency"), (CASE_IDS[1], "paired_residual"),
    (CASE_IDS[2], "separated_reconsideration_dependency"), (CASE_IDS[2], "paired_residual"), (CASE_IDS[2], "separated_decision_gap"),
    (CASE_IDS[3], "paired_residual"), (CASE_IDS[3], "separated_reconsideration_dependency"), (CASE_IDS[3], "separated_decision_gap"),
]


def _build_all() -> tuple[dict[str, bytes], dict[str, Any]]:
    support, cases, lookup = _build_support_files()
    by_key = {(row["case_id"], row["arm"]): row for row in lookup}
    call_plan = [{"ordinal": index, **copy.deepcopy(by_key[key])} for index, key in enumerate(ORDER, 1)]
    total_estimate = round(sum((row["estimated_input_tokens"] * 0.25 + row["maximum_output_tokens"] * 1.5) / 1_000_000 for row in call_plan), 9)
    case_estimates = {case_id: round(sum((row["estimated_input_tokens"] * 0.25 + row["maximum_output_tokens"] * 1.5) / 1_000_000 for row in call_plan if row["case_id"] == case_id), 9) for case_id in CASE_IDS}
    support_records = [_file_record(ROOT / relative, raw) for relative, raw in sorted(support.items())]
    execution_manifest = {
        "schema_version": "lolla.r4_separated_surface_execution_manifest.v1",
        "status": "frozen_runner_visible_inputs_no_authorization",
        "files": support_records,
        "protected_target_reference_present": False,
        "human_review_reference_present": False,
        "provider_calls": 0, "provider_cost_usd": 0.0,
    }
    execution_path = OUTPUT_ROOT / "execution-manifest.json"
    execution_raw = _render(execution_manifest)
    package_manifest = {
        "schema_version": "lolla.r4_separated_surface_package_manifest.v1",
        "status": "provider_free_generated_package_frozen",
        "files": support_records + [_file_record(execution_path, execution_raw)],
        "generated_file_count": len(support_records) + 1,
        "provider_calls": 0, "provider_cost_usd": 0.0,
    }
    package_path = OUTPUT_ROOT / "package-manifest.json"
    package_raw = _render(package_manifest)
    files = {**support, _relative(execution_path): execution_raw, _relative(package_path): package_raw}
    contract = {
        "schema_version": "lolla.r4_separated_surface_experiment_contract.v1",
        "status": "provider_free_design_frozen_no_authorization",
        "run_id": "lolla-r4-separated-surface-experiment-v1",
        "date": "2026-07-14", "scientific_question": "Does asking for the two existing residual surfaces in separate provider calls reduce unsupported opposite-surface companion records relative to asking for both surfaces together, while preserving genuine findings?",
        "cases": cases, "call_plan": call_plan, "operator": copy.deepcopy(OPERATOR),
        "current_provider_authorization": {"maximum_calls": 0, "maximum_cost_usd": 0.0, "authorization_artifact_exists": False},
        "budget": {
            "maximum_provider_calls": 12, "paired_calls": 4, "separated_calls": 8,
            "paired_maximum_output_tokens_per_case": 1600,
            "separated_maximum_output_tokens_per_call": 800,
            "separated_maximum_output_tokens_per_case": 1600,
            "duplicated_separated_input_cost_is_inherent_intervention_cost": True,
            "conservative_estimated_cost_by_case_usd": case_estimates,
            "conservative_estimated_total_cost_usd": total_estimate,
            "proposed_hard_provider_reported_cost_per_case_usd": 0.075,
            "proposed_hard_provider_reported_cost_total_usd": 0.30,
            "ceiling_purpose": "anomaly, duplicate-call, and loop stop; not scientific optimization",
            "automatic_retries": 0, "semantic_retries": 0, "fallback_models": 0,
            "model_substitutions": 0, "response_healing": False,
            "relationship_calls": 0, "evaluator_calls": 0, "embedding_calls": 0,
            "graph_calls": 0, "pipeline_calls": 0, "runtime_calls": 0,
        },
        "task_shape_intervention": {
            "paired": "one call requests both residual surfaces and returns two reviews",
            "separated": "two calls request one residual surface and return one review each",
            "allowed_differences": ["requested surface count", "returned review count", "provider call count", "singular grammar", "1600 versus 800+800 output allocation", "schema container and name changes required for one review"],
            "held_equal": ["complete source bytes", "complete prior bytes", "source aliases", "source-prior-task order", "task at end", "residual ontology and subtraction rules", "evidence authority and exact aliases", "zero and ambiguity semantics", "support and outcome enums", "record fields and per-surface bounds", "canonical surface mapping", "model", "provider route", "case seed", "reasoning", "strict JSON", "streaming", "privacy", "no retry or fallback"],
        },
        "deterministic_surface_to_canonical_role_mapping": {
            "residual_decision_gap": "unresolved_matter",
            "residual_reconsideration_dependency": "reopen_condition",
        },
        "execution_manifest": {"path": _relative(execution_path), "sha256": _sha_bytes(execution_raw)},
        "package_manifest": {"path": _relative(package_path), "sha256": _sha_bytes(package_raw)},
        "future_runner": {"path": _relative(RUNNER_PATH), "sha256": _sha(RUNNER_PATH), "transport_created_only_after_exact_authorization": True, "dry_run_constructs_transport": False},
        "authorization_shape": {"schema_version": "lolla.r4_separated_surface_experiment_authorization.v1", "one_use": True, "must_match_contract_and_all_twelve_request_hashes": True, "artifact_exists": False},
        "evaluation": {
            "scalar_score": None,
            "vector": ["mechanical execution and attribution", "quiet-control restraint", "genuine present sensitivity", "genuine future sensitivity", "opposite-surface companion behavior", "zero-versus-ambiguity", "evidence precision", "surface placement", "speaker and modal fidelity", "late evidence", "cost and custody"],
            "decision_matrix": {
                "task_shape_companion_pressure_supported": "Paired positives exhibit unsupported opposite-surface companions; separated calls remove them and preserve both genuine findings.",
                "separated_tasks_ineffective_companions_persist": "The same opposite-surface companions persist under separated calls.",
                "separated_tasks_overcorrected": "Separated calls lose either genuine Case 03 present finding or Case 04 future dependency.",
                "paired_arm_non_discriminating": "The paired arm does not reproduce companion behavior, so the matched comparison cannot isolate a separation advantage.",
                "mixed_or_insufficient_evidence": "Findings do not satisfy one clean causal pattern without a mechanical failure.",
                "semantic_result_not_evaluable": "Mechanical or custody failure prevents the full matched comparison."
            },
            "independent_blockers_even_if_supported": ["governed-threshold restraint", "scheduled-decision restraint", "assistant-proposal authority", "evidence selection and adjudication", "real-user usefulness"],
        },
        "historical_replay": {"case_count": 12, "case_artifact_links": 543, "unique_json_artifacts": 400},
        "provider_calls": 0, "provider_cost_usd": 0.0,
        "design_does_not_authorize_spending_execution_or_integration": True,
    }
    files[_relative(CONTRACT_PATH)] = _render(contract)
    return files, contract


def write() -> dict[str, Any]:
    files, _ = _build_all()
    for relative, raw in files.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return validate()


def validate() -> dict[str, Any]:
    files, contract = _build_all()
    for relative, raw in files.items():
        path = ROOT / relative
        if not path.is_file() or path.read_bytes() != raw:
            raise R4SeparatedSurfaceBuildError(f"generated artifact drifted: {relative}")
    if contract["provider_calls"] != 0 or contract["provider_cost_usd"] != 0.0:
        raise R4SeparatedSurfaceBuildError("provider-free boundary drifted")
    return {"status": "provider_free_separated_surface_experiment_valid", "case_count": 4, "request_count": 12, "paired_calls": 4, "separated_calls": 8, "provider_calls": 0, "provider_cost_usd": 0.0}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    if args.write == args.validate_only:
        parser.error("choose exactly one of --write or --validate-only")
    result = write() if args.write else validate()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
