#!/usr/bin/env python3
"""Gate 4 edge-probe experiment runner.

This is an offline evaluation harness. It does not import or change the live
Lolla runtime. The deterministic layer only loads archived Lane 4 routes,
retrieves compiled affordance records by model_id, assembles packets, validates
JSON shapes, and logs costs. Semantic activation and edge generation stay with
the boundary LLM.

Default mode should be `--dry-run` before any paid calls are made.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE_ROOT = Path.home() / ".local" / "share" / "lolla" / "runs"
DEFAULT_AFFORDANCES_PATH = Path("data/compiled/model_affordances/affordances_v3.json")
DEFAULT_OUTPUT_DIR = Path("data/evaluations/gate4_edge_probes")
DEFAULT_CASE_SELECTION_REPORT = Path("research/pr11-gate4-case-selection-2026-05-05.md")
DEFAULT_TOKEN_BUDGET = 40000
DEFAULT_SEED = 42
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_TIMEOUT_S = 240
DEFAULT_CASES = (
    "marcus-equity",
    "mother-deciding-address-year",
    "mid-level-consultant-report",
    "third-year-phd-student",
    "user-launch-independent-fintech",
    "year-old-oncologist-accept",
    "grant-equity-partnership-status",
    "founder-grant-marcus-equity",
    "mid-level-consultant-decides",
    "mother-deciding-protect-year",
)
EDGE_FIELD_SOURCES = {
    "do_not_use_when",
    "case_evidence_needed",
    "treatment_requirement",
    "misuse_guard",
    "diagnostic_question",
    "mechanism",
    "general_knowledge",
}
HIGH_VALUE_FIELD_SOURCES = {
    "do_not_use_when",
    "case_evidence_needed",
    "treatment_requirement",
    "misuse_guard",
}
ACTIVATION_STATUSES = {"activated", "set_aside", "unclear", "duplicate"}
CLARITY_COSTS = {"low", "medium", "high"}
EDGE_PROBE_OUTPUT_SCHEMA = {
    "case_id": "string",
    "route_id": "string",
    "arm": "B | C",
    "call_metadata": {
        "provider": "string",
        "model": "string",
        "input_tokens": "integer",
        "output_tokens": "integer",
        "cost_usd": "number",
    },
    "activation_calls": [
        {
            "model_id": "string",
            "affordance_id": "string",
            "activation_status": "activated | set_aside | unclear | duplicate",
            "case_quote": "exact case-context substring or empty string",
            "rationale": "string",
        }
    ],
    "edge_probes": [
        {
            "edge_probe": "string",
            "trace": {
                "model_id": "string",
                "affordance_id": "string",
                "field_source": (
                    "do_not_use_when | case_evidence_needed | treatment_requirement | "
                    "misuse_guard | diagnostic_question | mechanism | general_knowledge"
                ),
                "treatment_requirement_id": "string or null",
            },
            "why_this_is_edge": "string",
            "if_true_changes": "string",
            "dismissal_condition": "string",
            "clarity_cost": "low | medium | high",
        }
    ],
    "set_asides": [
        {
            "model_id": "string",
            "affordance_id": "string",
            "reason": "string",
        }
    ],
}


class Gate4ExperimentError(RuntimeError):
    """Raised when the Gate 4 experiment cannot proceed safely."""


@dataclass(frozen=True)
class RouteMaterial:
    case_id: str
    run_id: str
    result_path: Path
    route_id: str
    route_name: str
    candidate_model_ids: tuple[str, ...]
    covered_candidate_count: int
    total_candidate_count: int
    baseline_questions: tuple[str, ...]
    case_context: dict[str, str]

    @property
    def file_stem(self) -> str:
        return f"{_slug(self.case_id)}_{_slug(self.route_id)}"


@dataclass(frozen=True)
class PacketBuild:
    route: RouteMaterial
    arm: str
    packet: dict[str, Any]
    estimated_tokens: int
    included_model_ids: tuple[str, ...]
    missing_model_ids: tuple[str, ...] = ()
    budget_omitted_model_ids: tuple[str, ...] = ()

    @property
    def omitted_model_ids(self) -> tuple[str, ...]:
        return self.missing_model_ids + self.budget_omitted_model_ids


def _resolve_repo_path(path: Path) -> Path:
    path = Path(path).expanduser()
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    cleaned = cleaned.strip("-._")
    return cleaned or "route"


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _str(value: Any) -> str:
    return value if isinstance(value, str) else ""


def estimate_tokens(payload: Any) -> int:
    """Rough token estimate for cost gating; deliberately simple and stable."""
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return max(1, (len(text) + 3) // 4)


def load_dotenv(path: Path = REPO_ROOT / ".env") -> None:
    """Best-effort .env loader for ad-hoc evaluation runs."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value


def load_affordance_index(path: Path) -> dict[str, dict[str, Any]]:
    compiled = _load_json(path)
    records = _list(compiled.get("model_records"))
    index: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        model_id = _str(record.get("model_id"))
        if model_id:
            index[model_id] = record
    if not index:
        raise Gate4ExperimentError(f"No model_records found in {path}")
    return index


def affordance_ids_for_model(record: dict[str, Any]) -> set[str]:
    return {
        _str(affordance.get("affordance_id"))
        for affordance in _list(record.get("affordances"))
        if isinstance(affordance, dict) and _str(affordance.get("affordance_id"))
    }


def requirement_ids_for_affordance(
    index: dict[str, dict[str, Any]], model_id: str, affordance_id: str
) -> set[str]:
    record = index.get(model_id) or {}
    for affordance in _list(record.get("affordances")):
        if not isinstance(affordance, dict):
            continue
        if affordance.get("affordance_id") != affordance_id:
            continue
        return {
            _str(requirement.get("requirement_id"))
            for requirement in _list(affordance.get("treatment_requirements"))
            if isinstance(requirement, dict) and _str(requirement.get("requirement_id"))
        }
    return set()


def latest_result_path(archive_root: Path, case_slug: str) -> Path | None:
    case_dir = archive_root / case_slug
    if not case_dir.exists():
        return None
    runs = sorted(path for path in case_dir.iterdir() if path.is_dir())
    for run_dir in reversed(runs):
        result_path = run_dir / "result.json"
        if result_path.exists():
            return result_path
    return None


def extract_case_context(result: dict[str, Any]) -> dict[str, str]:
    """Extract the archived case material used in the edge-probe packet."""
    context: dict[str, str] = {}
    for key in ("query", "vanilla_answer"):
        value = _str(result.get(key)).strip()
        if value:
            context[key] = value
    extraction = _dict(result.get("extraction"))
    for key in (
        "decision_situation",
        "original_framing",
        "synthesized_position",
        "live_constraints",
        "dropped_threads",
        "reasoning_passages",
    ):
        if key in context:
            continue
        value = extraction.get(key)
        if isinstance(value, str) and value.strip():
            context[key] = value.strip()
        elif isinstance(value, (list, dict)) and value:
            context[key] = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if not context:
        raise Gate4ExperimentError(
            "Archived result has no query, vanilla_answer, or extraction context"
        )
    return context


def _gap_questions_by_dimension(card: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    questions: dict[str, tuple[str, ...]] = {}
    for row in _list(card.get("gap_questions")):
        if not isinstance(row, dict):
            continue
        dimension_id = _str(row.get("dimension_id"))
        if not dimension_id:
            continue
        deduped: list[str] = []
        seen: set[str] = set()
        for question in _list(row.get("questions")):
            text = _str(question).strip()
            if text and text not in seen:
                seen.add(text)
                deduped.append(text)
        questions[dimension_id] = tuple(deduped)
    return questions


def load_route_materials(
    *,
    archive_root: Path,
    cases: tuple[str, ...],
    affordance_index: dict[str, dict[str, Any]],
) -> tuple[list[RouteMaterial], list[dict[str, str]]]:
    materials: list[RouteMaterial] = []
    skipped: list[dict[str, str]] = []
    for case_slug in cases:
        result_path = latest_result_path(archive_root, case_slug)
        if result_path is None:
            skipped.append({"case_id": case_slug, "reason": "missing result.json"})
            continue
        result = _load_json(result_path)
        card = _dict(result.get("structural_coverage_card"))
        routes = _list(card.get("gap_routes"))
        if not routes:
            skipped.append({"case_id": case_slug, "reason": "missing gap_routes"})
            continue
        questions_by_dimension = _gap_questions_by_dimension(card)
        case_context = extract_case_context(result)
        run_id = result_path.parent.name
        for route in routes:
            if not isinstance(route, dict):
                continue
            route_id = _str(route.get("dimension_id"))
            if not route_id:
                continue
            candidate_model_ids = tuple(
                _str(model_id)
                for model_id in _list(route.get("candidate_model_ids"))
                if _str(model_id)
            )
            covered = sum(1 for model_id in candidate_model_ids if model_id in affordance_index)
            materials.append(
                RouteMaterial(
                    case_id=case_slug,
                    run_id=run_id,
                    result_path=result_path,
                    route_id=route_id,
                    route_name=_str(route.get("dimension_name")) or route_id,
                    candidate_model_ids=candidate_model_ids,
                    covered_candidate_count=covered,
                    total_candidate_count=len(candidate_model_ids),
                    baseline_questions=questions_by_dimension.get(route_id, ()),
                    case_context=case_context,
                )
            )
    return materials, skipped


def arm_a_output(route: RouteMaterial) -> dict[str, Any]:
    return {
        "case_id": route.case_id,
        "route_id": route.route_id,
        "arm": "A",
        "questions": list(route.baseline_questions),
    }


def base_packet(route: RouteMaterial) -> dict[str, Any]:
    return {
        "experiment": "gate4_edge_probe",
        "case_id": route.case_id,
        "run_id": route.run_id,
        "route_id": route.route_id,
        "route_name": route.route_name,
        "case_context": route.case_context,
        "gap_route": {
            "dimension_id": route.route_id,
            "dimension_name": route.route_name,
            "candidate_model_ids": list(route.candidate_model_ids),
        },
        "edge_probe_contract": {
            "edge_probe": "bounded pressure question that may expose a hidden failure",
            "why_this_is_edge": "why this is not central model restatement",
            "trace": "model/affordance/field source for the pressure",
            "if_true_changes": "what should change if the pressure is live",
            "dismissal_condition": "what evidence would safely dismiss the pressure",
        },
        "output_schema": EDGE_PROBE_OUTPUT_SCHEMA,
        "strict_output_rules": [
            "Return exactly one JSON object, not markdown.",
            "Use top-level key edge_probes, not probes.",
            "Every edge_probes item must contain a nested trace object.",
            "trace.field_source must be one of the listed enum values exactly.",
            "clarity_cost must be exactly low, medium, or high.",
            "Do not place model_id or affordance_id at the edge_probes item top level.",
            "Leave call_metadata as zeros if unavailable; the harness will overwrite it.",
        ],
    }


def build_arm_b_packet(
    route: RouteMaterial,
    affordance_index: dict[str, dict[str, Any]],
) -> PacketBuild:
    packet = base_packet(route)
    packet["arm"] = "B"
    packet["available_model_records"] = [
        {
            "model_id": model_id,
            "has_v3_record": model_id in affordance_index,
        }
        for model_id in route.candidate_model_ids
    ]
    packet["instructions"] = (
        "Generate edge probes using only the case context, the gap route, and "
        "the candidate model names. Do not assume access to compiled affordance "
        "records. Prefer constructive edge over encyclopedic explanation."
    )
    return PacketBuild(
        route=route,
        arm="B",
        packet=packet,
        estimated_tokens=estimate_tokens(packet),
        included_model_ids=(),
        missing_model_ids=(),
        budget_omitted_model_ids=(),
    )


def build_arm_c_packet(
    route: RouteMaterial,
    affordance_index: dict[str, dict[str, Any]],
    *,
    token_budget: int,
) -> PacketBuild:
    packet = base_packet(route)
    packet["arm"] = "C"
    packet["instructions"] = (
        "Generate edge probes using the compiled affordance records. Prefer "
        "peripheral-but-load-bearing operational constraints over central model "
        "definitions. High-value sources are do_not_use_when, "
        "case_evidence_needed, treatment_requirements, and misuse_guards. "
        "Make an activation call for every expected_activation_calls item."
    )
    records: list[dict[str, Any]] = []
    included: list[str] = []
    missing: list[str] = []
    budget_omitted: list[str] = []
    packet["affordance_records"] = records
    for model_id in route.candidate_model_ids:
        record = affordance_index.get(model_id)
        if record is None:
            missing.append(model_id)
            continue
        next_records = [*records, record]
        candidate_packet = {**packet, "affordance_records": next_records}
        if estimate_tokens(candidate_packet) > token_budget:
            budget_omitted.append(model_id)
            continue
        records.append(record)
        included.append(model_id)
    packet["affordance_records"] = records
    packet["missing_model_ids"] = missing
    packet["budget_omitted_model_ids"] = budget_omitted
    packet["expected_activation_calls"] = [
        {
            "model_id": model_id,
            "affordance_id": affordance_id,
        }
        for model_id, affordance_id in sorted(expected_activation_affordances(packet))
    ]
    return PacketBuild(
        route=route,
        arm="C",
        packet=packet,
        estimated_tokens=estimate_tokens(packet),
        included_model_ids=tuple(included),
        missing_model_ids=tuple(missing),
        budget_omitted_model_ids=tuple(budget_omitted),
    )


def expected_activation_affordances(packet: dict[str, Any]) -> set[tuple[str, str]]:
    expected: set[tuple[str, str]] = set()
    for record in _list(packet.get("affordance_records")):
        if not isinstance(record, dict):
            continue
        model_id = _str(record.get("model_id"))
        for affordance in _list(record.get("affordances")):
            if not isinstance(affordance, dict):
                continue
            affordance_id = _str(affordance.get("affordance_id"))
            if model_id and affordance_id:
                expected.add((model_id, affordance_id))
    return expected


def validate_arm_a_output(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("arm") != "A":
        errors.append("arm must be A")
    for key in ("case_id", "route_id"):
        if not _str(payload.get(key)):
            errors.append(f"{key} must be a non-empty string")
    questions = payload.get("questions")
    if not isinstance(questions, list) or not all(isinstance(item, str) for item in questions):
        errors.append("questions must be a list of strings")
    return errors


def validate_trace_ids(
    trace: dict[str, Any],
    affordance_index: dict[str, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    model_id = _str(trace.get("model_id"))
    affordance_id = _str(trace.get("affordance_id"))
    field_source = _str(trace.get("field_source"))
    if field_source not in EDGE_FIELD_SOURCES:
        errors.append(f"invalid field_source: {field_source!r}")
    if not model_id:
        errors.append("trace.model_id must be non-empty")
        return errors
    record = affordance_index.get(model_id)
    if record is None:
        errors.append(f"unknown trace.model_id: {model_id}")
        return errors
    affordance_ids = affordance_ids_for_model(record)
    if not affordance_id:
        errors.append("trace.affordance_id must be non-empty")
    elif affordance_id not in affordance_ids:
        errors.append(f"unknown trace.affordance_id for {model_id}: {affordance_id}")
    if field_source == "treatment_requirement":
        requirement_id = trace.get("treatment_requirement_id")
        if not isinstance(requirement_id, str) or not requirement_id:
            errors.append("treatment_requirement trace requires treatment_requirement_id")
        elif requirement_id not in requirement_ids_for_affordance(
            affordance_index, model_id, affordance_id
        ):
            errors.append(
                f"unknown treatment_requirement_id for {affordance_id}: {requirement_id}"
            )
    return errors


def _case_context_text(case_context: dict[str, str]) -> str:
    return "\n\n".join(value for value in case_context.values() if isinstance(value, str))


def validate_edge_probe_output(
    payload: dict[str, Any],
    *,
    expected_arm: str,
    affordance_index: dict[str, dict[str, Any]],
    require_verified_traces: bool,
    expected_activation_ids: set[tuple[str, str]] | None = None,
    case_context: dict[str, str] | None = None,
) -> list[str]:
    errors: list[str] = []
    if payload.get("arm") != expected_arm:
        errors.append(f"arm must be {expected_arm}")
    for key in ("case_id", "route_id"):
        if not _str(payload.get(key)):
            errors.append(f"{key} must be a non-empty string")
    metadata = _dict(payload.get("call_metadata"))
    for key in ("provider", "model"):
        if not _str(metadata.get(key)):
            errors.append(f"call_metadata.{key} must be a non-empty string")
    for key in ("input_tokens", "output_tokens"):
        if not isinstance(metadata.get(key), int):
            errors.append(f"call_metadata.{key} must be an integer")
    if not isinstance(metadata.get("cost_usd"), (int, float)):
        errors.append("call_metadata.cost_usd must be a number")

    seen_activation_ids: set[tuple[str, str]] = set()
    context_text = _case_context_text(case_context or {})
    activation_calls = payload.get("activation_calls")
    if not isinstance(activation_calls, list):
        errors.append("activation_calls must be a list")
    else:
        for index, call in enumerate(activation_calls):
            call_map = _dict(call)
            model_id = _str(call_map.get("model_id"))
            affordance_id = _str(call_map.get("affordance_id"))
            if not model_id:
                errors.append(f"activation_calls[{index}].model_id must be non-empty")
            if not affordance_id:
                errors.append(f"activation_calls[{index}].affordance_id must be non-empty")
            if _str(call_map.get("activation_status")) not in ACTIVATION_STATUSES:
                errors.append(f"activation_calls[{index}].activation_status is invalid")
            quote = _str(call_map.get("case_quote"))
            if quote and context_text and quote not in context_text:
                errors.append(f"activation_calls[{index}].case_quote is not exact")
            if require_verified_traces and model_id and affordance_id:
                trace_errors = validate_trace_ids(
                    {
                        "model_id": model_id,
                        "affordance_id": affordance_id,
                        "field_source": "mechanism",
                    },
                    affordance_index,
                )
                errors.extend(
                    f"activation_calls[{index}].{error}" for error in trace_errors
                )
            if model_id and affordance_id:
                seen_activation_ids.add((model_id, affordance_id))

    if expected_activation_ids is not None:
        missing = sorted(expected_activation_ids - seen_activation_ids)
        if missing:
            errors.append(f"missing activation_calls for included affordances: {missing[:8]}")

    edge_probes = payload.get("edge_probes")
    if not isinstance(edge_probes, list):
        errors.append("edge_probes must be a list")
    else:
        for index, probe in enumerate(edge_probes):
            probe_map = _dict(probe)
            for key in (
                "edge_probe",
                "why_this_is_edge",
                "if_true_changes",
                "dismissal_condition",
            ):
                if not _str(probe_map.get(key)):
                    errors.append(f"edge_probes[{index}].{key} must be non-empty")
            if _str(probe_map.get("clarity_cost")) not in CLARITY_COSTS:
                errors.append(f"edge_probes[{index}].clarity_cost is invalid")
            trace = _dict(probe_map.get("trace"))
            if require_verified_traces:
                errors.extend(
                    f"edge_probes[{index}].trace.{error}"
                    for error in validate_trace_ids(trace, affordance_index)
                )
            elif _str(trace.get("field_source")) not in EDGE_FIELD_SOURCES:
                errors.append(f"edge_probes[{index}].trace.field_source is invalid")

    set_asides = payload.get("set_asides")
    if not isinstance(set_asides, list):
        errors.append("set_asides must be a list")
    else:
        for index, item in enumerate(set_asides):
            item_map = _dict(item)
            for key in ("model_id", "affordance_id", "reason"):
                if not _str(item_map.get(key)):
                    errors.append(f"set_asides[{index}].{key} must be non-empty")
    return errors


def dedupe_edge_probe_output(payload: dict[str, Any]) -> dict[str, Any]:
    probes = payload.get("edge_probes")
    if not isinstance(probes, list):
        return payload
    seen: set[str] = set()
    deduped: list[Any] = []
    for probe in probes:
        if not isinstance(probe, dict):
            deduped.append(probe)
            continue
        text = _str(probe.get("edge_probe")).strip()
        if text and text in seen:
            continue
        if text:
            seen.add(text)
        deduped.append(probe)
    payload = dict(payload)
    payload["edge_probes"] = deduped
    return payload


EDGE_PROBE_SYSTEM_PROMPT = """\
You are generating Gate 4 edge probes for an offline Lolla evaluation.

An edge probe is a bounded pressure that may expose a hidden failure in the
current reasoning trajectory. It is not a restatement of what a mental model
means. It must include:
1. the probe,
2. why it is an edge,
3. the source field it traces to,
4. what changes if the edge is true,
5. how to dismiss it if false.

Return only JSON matching the requested schema. Do not include markdown.

Strictness matters more than eloquence. Use the exact enum values in the packet.
If a field is uncertain, still include the field with an allowed enum value and
explain the uncertainty in the rationale.
"""


def call_openrouter_json(
    *,
    api_key: str,
    model: str,
    system_prompt: str,
    user_packet: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_packet, ensure_ascii=False)},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=OPENROUTER_TIMEOUT_S) as resp:
            response = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body_preview = exc.read().decode(errors="replace")[:800]
        raise Gate4ExperimentError(f"OpenRouter HTTP {exc.code}: {body_preview}") from exc

    choices = _list(response.get("choices"))
    if not choices:
        raise Gate4ExperimentError("OpenRouter response has no choices")
    content = _dict(_dict(choices[0]).get("message")).get("content", "")
    if isinstance(content, list):
        content = "\n".join(
            _str(part.get("text")) for part in content if isinstance(part, dict)
        )
    text = _str(content).strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise Gate4ExperimentError(f"Model returned non-JSON content: {text[:1000]}") from exc

    usage = _dict(response.get("usage"))
    metadata = {
        "provider": "openrouter",
        "model": model,
        "input_tokens": int(usage.get("prompt_tokens") or 0),
        "output_tokens": int(usage.get("completion_tokens") or 0),
        "cost_usd": float(usage.get("cost") or usage.get("total_cost") or 0.0),
    }
    return payload, metadata


def normalize_edge_probe_payload(
    payload: dict[str, Any],
    *,
    route: RouteMaterial,
    arm: str,
    call_metadata: dict[str, Any],
) -> dict[str, Any]:
    normalized = dict(payload)
    normalized["case_id"] = route.case_id
    normalized["route_id"] = route.route_id
    normalized["arm"] = arm
    normalized["call_metadata"] = call_metadata
    normalized.setdefault("activation_calls", [])
    normalized.setdefault("edge_probes", [])
    normalized.setdefault("set_asides", [])
    return dedupe_edge_probe_output(normalized)


def run_llm_arm(
    *,
    provider: str,
    model: str,
    route: RouteMaterial,
    arm: str,
    packet: dict[str, Any],
) -> dict[str, Any]:
    if provider != "openrouter":
        raise Gate4ExperimentError("Only --provider openrouter is implemented for PR11")
    if not model:
        raise Gate4ExperimentError("--model is required for non-dry-run calls")
    load_dotenv()
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise Gate4ExperimentError(
            "Missing OpenRouter API key: set LOLLA_OPENROUTER_API_KEY or OPENROUTER_API_KEY"
        )
    payload, metadata = call_openrouter_json(
        api_key=api_key,
        model=model,
        system_prompt=EDGE_PROBE_SYSTEM_PROMPT,
        user_packet=packet,
    )
    return normalize_edge_probe_payload(
        payload,
        route=route,
        arm=arm,
        call_metadata=metadata,
    )


def render_case_selection_report(
    *,
    materials: list[RouteMaterial],
    skipped: list[dict[str, str]],
    cases: tuple[str, ...],
    affordance_record_count: int,
) -> str:
    by_case: dict[str, dict[str, Any]] = {}
    for route in materials:
        entry = by_case.setdefault(
            route.case_id,
            {
                "run_id": route.run_id,
                "route_count": 0,
                "covered": 0,
                "total": 0,
                "routes": [],
            },
        )
        entry["route_count"] += 1
        entry["covered"] += route.covered_candidate_count
        entry["total"] += route.total_candidate_count
        entry["routes"].append(route.route_id)
    total_covered = sum(entry["covered"] for entry in by_case.values())
    total_candidates = sum(entry["total"] for entry in by_case.values())
    fraction = (total_covered / total_candidates * 100.0) if total_candidates else 0.0
    lines = [
        "# PR 11 Gate 4 Case Selection",
        "",
        f"**Date:** {datetime.now(timezone.utc).date().isoformat()}",
        "**Status:** Dry-run case-selection artifact; not measurement results.",
        "",
        "This artifact records the archived cases and Lane 4 routes used for the Gate 4 edge-probe experiment. Coverage is candidate-appearance coverage: every candidate model listed on every gap route counts once.",
        "",
        "## Summary",
        "",
        f"- Requested cases: `{len(cases)}`",
        f"- Usable cases: `{len(by_case)}`",
        f"- Gap routes: `{len(materials)}`",
        f"- Compiled v3 model records available: `{affordance_record_count}`",
        f"- v3-covered candidate appearances: `{total_covered}/{total_candidates}` ({fraction:.1f}%)",
        "",
        "## Cases",
        "",
        "| Case slug | Run timestamp | Routes | v3-covered / candidates | Covered % |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for case_id in cases:
        entry = by_case.get(case_id)
        if entry is None:
            lines.append(f"| `{case_id}` | skipped | 0 | 0/0 | 0.0% |")
            continue
        covered = int(entry["covered"])
        total = int(entry["total"])
        pct = (covered / total * 100.0) if total else 0.0
        lines.append(
            f"| `{case_id}` | `{entry['run_id']}` | {entry['route_count']} | {covered}/{total} | {pct:.1f}% |"
        )
    lines.extend(["", "## Per-Route Detail", ""])
    for route in materials:
        pct = (
            route.covered_candidate_count / route.total_candidate_count * 100.0
            if route.total_candidate_count
            else 0.0
        )
        lines.append(
            f"- `{route.case_id}` / `{route.route_id}`: "
            f"{route.covered_candidate_count}/{route.total_candidate_count} covered ({pct:.1f}%). "
            f"Candidates: {', '.join(route.candidate_model_ids)}"
        )
    if skipped:
        lines.extend(["", "## Skips", ""])
        for item in skipped:
            lines.append(f"- `{item['case_id']}`: {item['reason']}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This selection artifact does not run Arm B, Arm C, or judge calls. It only verifies archived route availability and v3 affordance-record coverage before cost approval.",
            "",
        ]
    )
    return "\n".join(lines)


def _usage_totals(records: list[dict[str, Any]]) -> dict[str, Any]:
    input_tokens = 0
    output_tokens = 0
    cost_usd = 0.0
    for record in records:
        metadata = _dict(record.get("call_metadata"))
        input_tokens += int(metadata.get("input_tokens") or 0)
        output_tokens += int(metadata.get("output_tokens") or 0)
        cost_usd += float(metadata.get("cost_usd") or 0.0)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_usd": round(cost_usd, 6),
    }


def write_experiment_outputs(
    *,
    materials: list[RouteMaterial],
    skipped: list[dict[str, str]],
    requested_cases: tuple[str, ...],
    affordance_index: dict[str, dict[str, Any]],
    output_dir: Path,
    report_path: Path,
    arms: set[str],
    token_budget: int,
    provider: str,
    model: str,
    dry_run: bool,
    seed: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    call_records: list[dict[str, Any]] = []
    packet_builds: list[PacketBuild] = []
    validation_errors: list[str] = []

    for route in materials:
        if "A" in arms:
            payload = arm_a_output(route)
            errors = validate_arm_a_output(payload)
            validation_errors.extend(f"{route.file_stem} arm A: {error}" for error in errors)
            _write_json(output_dir / "arm_a" / f"{route.file_stem}.json", payload)

        if "B" in arms:
            packet_b = build_arm_b_packet(route, affordance_index)
            packet_builds.append(packet_b)
            _write_json(output_dir / "packets" / "arm_b" / f"{route.file_stem}.json", packet_b.packet)
            if not dry_run:
                payload_b = run_llm_arm(
                    provider=provider,
                    model=model,
                    route=route,
                    arm="B",
                    packet=packet_b.packet,
                )
                errors = validate_edge_probe_output(
                    payload_b,
                    expected_arm="B",
                    affordance_index=affordance_index,
                    require_verified_traces=False,
                    case_context=route.case_context,
                )
                validation_errors.extend(
                    f"{route.file_stem} arm B: {error}" for error in errors
                )
                _write_json(output_dir / "arm_b" / f"{route.file_stem}.json", payload_b)
                call_records.append(payload_b)

        if "C" in arms:
            packet_c = build_arm_c_packet(route, affordance_index, token_budget=token_budget)
            packet_builds.append(packet_c)
            _write_json(output_dir / "packets" / "arm_c" / f"{route.file_stem}.json", packet_c.packet)
            if not dry_run:
                payload_c = run_llm_arm(
                    provider=provider,
                    model=model,
                    route=route,
                    arm="C",
                    packet=packet_c.packet,
                )
                errors = validate_edge_probe_output(
                    payload_c,
                    expected_arm="C",
                    affordance_index=affordance_index,
                    require_verified_traces=True,
                    expected_activation_ids=expected_activation_affordances(packet_c.packet),
                    case_context=route.case_context,
                )
                validation_errors.extend(
                    f"{route.file_stem} arm C: {error}" for error in errors
                )
                _write_json(output_dir / "arm_c" / f"{route.file_stem}.json", payload_c)
                call_records.append(payload_c)

    report = render_case_selection_report(
        materials=materials,
        skipped=skipped,
        cases=requested_cases,
        affordance_record_count=len(affordance_index),
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    expected_llm_call_count = len(materials) * len({"B", "C"} & arms)
    token_estimates_by_arm = {
        arm: sum(build.estimated_tokens for build in packet_builds if build.arm == arm)
        for arm in ("B", "C")
    }
    omitted_by_route = [
        {
            "case_id": build.route.case_id,
            "route_id": build.route.route_id,
            "arm": build.arm,
            "included_model_ids": list(build.included_model_ids),
            "missing_model_ids": list(build.missing_model_ids),
            "budget_omitted_model_ids": list(build.budget_omitted_model_ids),
            "omitted_model_ids": list(build.omitted_model_ids),
            "estimated_tokens": build.estimated_tokens,
        }
        for build in packet_builds
        if build.omitted_model_ids or build.arm == "C"
    ]
    summary = {
        "status": "dry_run" if dry_run else "completed",
        "dry_run": dry_run,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "case_count": len({route.case_id for route in materials}),
        "route_count": len(materials),
        "arms": sorted(arms),
        "expected_llm_call_count": expected_llm_call_count,
        "expected_judge_call_count": len(materials),
        "token_budget_per_call": token_budget,
        "packet_token_estimates_by_arm": token_estimates_by_arm,
        "max_packet_tokens": max((build.estimated_tokens for build in packet_builds), default=0),
        "provider": provider,
        "model": model,
        "usage_totals": _usage_totals(call_records),
        "skipped": skipped,
        "omissions": omitted_by_route,
        "validation_errors": validation_errors,
        "case_selection_report": str(report_path.relative_to(REPO_ROOT) if report_path.is_relative_to(REPO_ROOT) else report_path),
    }
    _write_json(output_dir / "summary.json", summary)
    if validation_errors:
        raise Gate4ExperimentError(
            "Validation errors:\n" + "\n".join(validation_errors[:20])
        )
    return summary


def parse_arms(value: str) -> set[str]:
    arms = {part.strip().upper() for part in value.split(",") if part.strip()}
    allowed = {"A", "B", "C"}
    unknown = arms - allowed
    if unknown:
        raise argparse.ArgumentTypeError(f"Unknown arms: {sorted(unknown)}")
    if not arms:
        raise argparse.ArgumentTypeError("At least one arm is required")
    return arms


def parse_cases(value: str | None) -> tuple[str, ...]:
    if not value:
        return DEFAULT_CASES
    cases = tuple(part.strip() for part in value.split(",") if part.strip())
    if not cases:
        raise argparse.ArgumentTypeError("At least one case slug is required")
    return cases


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-root", type=Path, default=DEFAULT_ARCHIVE_ROOT)
    parser.add_argument("--affordances-path", type=Path, default=DEFAULT_AFFORDANCES_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--case-selection-report", type=Path, default=DEFAULT_CASE_SELECTION_REPORT)
    parser.add_argument("--cases", default="")
    parser.add_argument("--arms", type=parse_arms, default=parse_arms("A,B,C"))
    parser.add_argument("--token-budget", type=int, default=DEFAULT_TOKEN_BUDGET)
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--model", default=os.getenv("LOLLA_GATE4_MODEL", ""))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    archive_root = Path(args.archive_root).expanduser()
    affordances_path = _resolve_repo_path(args.affordances_path)
    output_dir = _resolve_repo_path(args.output_dir)
    report_path = _resolve_repo_path(args.case_selection_report)
    cases = parse_cases(args.cases)

    if args.token_budget <= 0:
        parser.error("--token-budget must be positive")
    if not args.dry_run and {"B", "C"} & set(args.arms) and not args.model:
        parser.error("--model is required for non-dry-run Arm B/C calls")

    try:
        affordance_index = load_affordance_index(affordances_path)
        materials, skipped = load_route_materials(
            archive_root=archive_root,
            cases=cases,
            affordance_index=affordance_index,
        )
        if not materials:
            raise Gate4ExperimentError("No usable case routes found")
        summary = write_experiment_outputs(
            materials=materials,
            skipped=skipped,
            requested_cases=cases,
            affordance_index=affordance_index,
            output_dir=output_dir,
            report_path=report_path,
            arms=set(args.arms),
            token_budget=args.token_budget,
            provider=args.provider,
            model=args.model,
            dry_run=args.dry_run,
            seed=args.seed,
        )
    except Gate4ExperimentError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    mode = "DRY RUN" if args.dry_run else "COMPLETE"
    print(f"{mode}: {summary['case_count']} cases, {summary['route_count']} routes")
    print(f"Expected Arm B/C calls: {summary['expected_llm_call_count']}")
    print(f"Expected judge calls: {summary['expected_judge_call_count']}")
    print(f"Max packet estimate: {summary['max_packet_tokens']} tokens")
    print(f"Summary: {output_dir / 'summary.json'}")
    print(f"Case selection report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
