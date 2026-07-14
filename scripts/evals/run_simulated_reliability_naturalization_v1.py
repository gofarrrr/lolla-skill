#!/usr/bin/env python3
"""Create naturalistic source proposals from frozen semantic skeletons.

This is source authoring, not a Lolla run or evaluator. It makes at most one
OpenRouter call per case, preserves every attempted call, and never repairs or
selects a proposal automatically.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import statistics
import time
from pathlib import Path
from typing import Any, Mapping
from urllib import error, request


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_SCHEMA = "lolla.simulated_reliability_naturalization_contract.v1"
SYSTEM_PROMPT = """You are a source-dialogue editor, not an evaluator. Rewrite a synthetic decision conversation so it resembles a plausible extended exchange between one user and one capable LLM. Preserve every material fact, stakeholder, constraint, uncertainty, change of position, provisional decision, later complication, and final decision boundary from the supplied semantic skeleton. Do not improve the reasoning toward a hidden answer and do not add facts, numbers, people, events, or domain expertise. Make the voices distinct. Vary turn length and pacing. Allow partial answers, hesitation, clarification, one useful assistant overreach or incomplete frame followed by grounded repair, and a temporarily dropped thread that returns naturally. The assistant should remain helpful, not incompetent. Do not add fake spelling mistakes, slang caricature, mental-model names, evaluation language, or references to this editing task. Return exactly 24 messages: 12 USER and 12 ASSISTANT messages in strict alternating order beginning with USER."""
RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "messages": {
            "type": "array",
            "minItems": 24,
            "maxItems": 24,
            "items": {
                "type": "object",
                "properties": {
                    "role": {"type": "string", "enum": ["USER", "ASSISTANT"]},
                    "text": {"type": "string", "minLength": 1, "maxLength": 2500},
                },
                "required": ["role", "text"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["messages"],
    "additionalProperties": False,
}
FORBIDDEN = {
    "lolla": re.compile(r"\blolla\b", re.IGNORECASE),
    "mental_model": re.compile(r"\bmental[ -]models?\b", re.IGNORECASE),
    "evaluation": re.compile(r"\b(?:benchmark|gold answer|expected pressure|evaluation corpus)\b", re.IGNORECASE),
    "editing_task": re.compile(r"\b(?:semantic skeleton|source-dialogue editor|editing task)\b", re.IGNORECASE),
}


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _json_sha(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _load_env(path: Path) -> None:
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"").strip("'"))


def _user_prompt(case_id: str, source: str) -> str:
    return (
        "NATURALIZE THIS CONVERSATION\n"
        f"Case identity: {case_id}\n\n"
        "The text below is authoritative for semantic content but not for style. "
        "Return only the rewritten message sequence in the required schema. "
        "Preserve its final meaning without copying its uniform paragraph rhythm.\n\n"
        "SOURCE SEMANTIC SKELETON\n"
        + source
    )


def _coefficient(values: list[int]) -> float:
    mean = statistics.mean(values)
    return statistics.pstdev(values) / mean if mean else 0.0


def _proposal_review(candidate: object) -> dict[str, Any]:
    issues: list[str] = []
    if not isinstance(candidate, Mapping) or set(candidate) != {"messages"}:
        return {"status": "reject", "issues": ["response_envelope_invalid"]}
    messages = candidate.get("messages")
    if not isinstance(messages, list) or len(messages) != 24:
        return {"status": "reject", "issues": ["message_count_not_24"]}
    expected = [role for _ in range(12) for role in ("USER", "ASSISTANT")]
    observed: list[str] = []
    lengths: dict[str, list[int]] = {"USER": [], "ASSISTANT": []}
    combined: list[str] = []
    for index, value in enumerate(messages):
        if not isinstance(value, Mapping) or set(value) != {"role", "text"}:
            issues.append(f"message_{index + 1}_shape_invalid")
            continue
        role = str(value.get("role", ""))
        text = str(value.get("text", "")).strip()
        observed.append(role)
        if role not in lengths:
            issues.append(f"message_{index + 1}_role_invalid")
        elif not text:
            issues.append(f"message_{index + 1}_empty")
        else:
            lengths[role].append(len(text.split()))
            combined.append(text)
    if observed != expected:
        issues.append("role_alternation_invalid")
    full_text = "\n".join(combined)
    for name, pattern in FORBIDDEN.items():
        if pattern.search(full_text):
            issues.append(f"{name}_leakage")
    total_words = len(full_text.split())
    if not 1300 <= total_words <= 2800:
        issues.append("total_word_count_outside_1300_2800")
    diagnostics: dict[str, Any] = {"total_words": total_words}
    for role in ("USER", "ASSISTANT"):
        values = lengths[role]
        if len(values) != 12:
            continue
        diagnostics[role.lower()] = {
            "minimum_words": min(values),
            "maximum_words": max(values),
            "mean_words": round(statistics.mean(values), 3),
            "coefficient_of_variation": round(_coefficient(values), 4),
        }
        if min(values) > 45:
            issues.append(f"{role.lower()}_has_no_short_turn")
        required_max = 100 if role == "USER" else 90
        if max(values) < required_max:
            issues.append(f"{role.lower()}_has_no_long_turn")
        if _coefficient(values) < 0.25:
            issues.append(f"{role.lower()}_length_variation_below_diagnostic_floor")
    return {
        "status": "provider_free_shape_pass_semantic_review_required" if not issues else "reject",
        "issues": issues,
        "diagnostics": diagnostics,
    }


def _validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise RuntimeError("contract schema mismatch")
    if contract.get("status") != "frozen_before_at_most_twelve_no_retry_source_calls":
        raise RuntimeError("contract is not frozen")
    budget = contract.get("budget", {})
    if budget.get("maximum_provider_calls") != 12 or budget.get("automatic_retries") != 0:
        raise RuntimeError("invalid call budget")
    config = contract.get("call_configuration", {})
    if config.get("model") != "google/gemini-3.1-flash-lite":
        raise RuntimeError("unexpected source editor model")
    if config.get("provider") != "openrouter":
        raise RuntimeError("source editor must use OpenRouter")
    if contract.get("system_prompt_sha256") != hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest():
        raise RuntimeError("system prompt drifted")
    if contract.get("response_schema_sha256") != _json_sha(RESPONSE_SCHEMA):
        raise RuntimeError("response schema drifted")
    cases = contract.get("cases")
    if not isinstance(cases, list) or len(cases) != 12:
        raise RuntimeError("expected 12 source cases")
    for row in cases:
        path = ROOT / row["source_path"]
        if _file_sha(path) != row["source_sha256"]:
            raise RuntimeError(f"source drifted: {path}")
        source = path.read_text(encoding="utf-8")
        if hashlib.sha256(_user_prompt(row["case_id"], source).encode()).hexdigest() != row["user_prompt_sha256"]:
            raise RuntimeError(f"user prompt drifted: {row['case_id']}")


def _extract_candidate(payload: Mapping[str, Any]) -> tuple[object, str]:
    choices = payload.get("choices") if isinstance(payload.get("choices"), list) else []
    choice = choices[0] if choices and isinstance(choices[0], Mapping) else {}
    message = choice.get("message") if isinstance(choice.get("message"), Mapping) else {}
    content = str(message.get("content", ""))
    try:
        return json.loads(content), content
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        if start >= 0 and end > start:
            return json.loads(content[start : end + 1]), content
        raise


def _run_case(contract: Mapping[str, Any], row: Mapping[str, Any], output: Path) -> dict[str, Any]:
    config = contract["call_configuration"]
    source = (ROOT / row["source_path"]).read_text(encoding="utf-8")
    prompt = _user_prompt(row["case_id"], source)
    started = time.monotonic()
    base = {
        "case_id": row["case_id"],
        "source_path": row["source_path"],
        "source_sha256": row["source_sha256"],
        "system_prompt_sha256": contract["system_prompt_sha256"],
        "user_prompt_sha256": row["user_prompt_sha256"],
        "response_schema_sha256": contract["response_schema_sha256"],
        "requested_model": config["model"],
        "seed": row["seed"],
        "temperature": config["temperature"],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "source_authoring_call": True,
        "lolla_pipeline_call": False,
        "evaluator_call": False,
    }
    body = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": f"lolla_v1_source_{row['case_id'].replace('-', '_')}",
                "strict": True,
                "schema": RESPONSE_SCHEMA,
            },
        },
        "provider": {"require_parameters": True, "allow_fallbacks": False},
        "temperature": config["temperature"],
        "seed": row["seed"],
        "max_tokens": config["max_output_tokens"],
        "reasoning": {"enabled": False},
    }
    key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not key:
        return {**base, "operational_status": "missing_api_key", "provider_calls": 0}
    req = request.Request(
        config["endpoint"],
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=config["provider_timeout_seconds"]) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return {
            **base,
            "operational_status": f"http_error_{exc.code}",
            "provider_calls": 1,
            "error_sha256": hashlib.sha256(raw.encode()).hexdigest(),
            "error_excerpt": raw[:1000],
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            **base,
            "operational_status": "transport_error",
            "provider_calls": 1,
            "error_type": type(exc).__name__,
            "error_message": str(exc)[:1000],
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    candidate: object = None
    parse_error = ""
    try:
        candidate, _raw = _extract_candidate(payload)
    except Exception as exc:  # noqa: BLE001
        parse_error = f"{type(exc).__name__}: {exc}"
    review = _proposal_review(candidate)
    usage = payload.get("usage") if isinstance(payload.get("usage"), Mapping) else {}
    result = {
        **base,
        "operational_status": "ok" if candidate is not None else "invalid_response",
        "provider_calls": 1,
        "served_model": str(payload.get("model", "")),
        "served_provider": str(payload.get("provider", "")),
        "finish_reason": str((payload.get("choices") or [{}])[0].get("finish_reason", "")),
        "candidate": candidate,
        "candidate_sha256": _json_sha(candidate) if candidate is not None else "",
        "parse_error": parse_error,
        "provider_free_shape_review": review,
        "semantic_and_naturalism_review": "pending",
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "provider_reported_cost_usd": usage.get("cost"),
        "provider_payload_sha256": _json_sha(payload),
        "duration_seconds": round(time.monotonic() - started, 3),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract = _load_json(args.contract.resolve())
    _validate_contract(contract)
    if args.dry_run:
        print(json.dumps({"status": "contract_valid", "provider_calls": 0}, indent=2))
        return 0
    output = args.output_dir.resolve()
    if not output.is_dir() or (output / "result.json").exists() or list(output.glob("call-*-started.json")):
        raise RuntimeError("output directory absent, complete, or already started")
    if args.env_file:
        _load_env(args.env_file.resolve())
    calls: list[dict[str, Any]] = []
    for index, row in enumerate(contract["cases"], 1):
        _write_json(
            output / f"call-{index:02d}-started.json",
            {"case_id": row["case_id"], "seed": row["seed"], "automatic_retries": 0},
        )
        result = _run_case(contract, row, output)
        _write_json(output / f"call-{index:02d}-result.json", result)
        calls.append(result)
    total_cost = sum(
        float(row["provider_reported_cost_usd"])
        for row in calls
        if isinstance(row.get("provider_reported_cost_usd"), (int, float))
        and math.isfinite(float(row["provider_reported_cost_usd"]))
    )
    summary = {
        "schema_version": "lolla.simulated_reliability_naturalization_result.v1",
        "status": "source_proposals_preserved_review_required",
        "provider_request_count": sum(int(row.get("provider_calls", 0)) for row in calls),
        "operational_ok_count": sum(row.get("operational_status") == "ok" for row in calls),
        "shape_pass_count": sum(
            row.get("provider_free_shape_review", {}).get("status")
            == "provider_free_shape_pass_semantic_review_required"
            for row in calls
        ),
        "provider_reported_cost_usd": round(total_cost, 12),
        "automatic_retries": 0,
        "semantic_and_naturalism_review": "pending_for_every_proposal",
        "no_proposal_automatically_admitted": True,
    }
    _write_json(output / "result.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
