#!/usr/bin/env python3
"""Freeze and run fresh-context synthesis over complete harvested ledgers."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib import error, request

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.conversation_event_harvesting import (  # noqa: E402
    build_synthesis_contract,
    parse_synthesis,
)
from engine.system_b.conversation_event_pipeline import (  # noqa: E402
    build_synthesis_ledger,
    compile_handoff_from_event_ledgers,
)
from engine.system_b.conversation_state_candidates import build_source_catalog  # noqa: E402
from engine.system_b.conversation_state_handoff import (  # noqa: E402
    build_fact_free_routing_boundary,
    validate_conversation_state_handoff,
)
from engine.system_b.pricing import estimate_chat_cost_usd, lookup_chat_price  # noqa: E402
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402
from scripts.evals.run_fixed_safe_holdout_pool import (  # noqa: E402
    _extract_json_object,
    _model_attribution,
)


MODEL = "google/gemini-3.1-flash-lite"
FAMILIES = ("positions", "threads", "constraints")
CONTRACT_SCHEMA = "lolla.conversation_event_synthesis_contract.v1"
AUTHORIZATION_SCHEMA = "lolla.conversation_event_synthesis_authorization.v1"
CALL_SCHEMA = "lolla.conversation_event_synthesis_call.v1"
RESULT_SCHEMA = "lolla.conversation_event_synthesis_phase_result.v1"


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def _case_spec(event_ledger_path: Path) -> dict[str, Any]:
    ledger = json.loads(event_ledger_path.read_text())
    source_path = ROOT / ledger["source"]["path"]
    return {
        "case_id": ledger["case_id"],
        "event_ledger_path": str(event_ledger_path.relative_to(ROOT)),
        "event_ledger_sha256": _file_sha(event_ledger_path),
        "source_path": ledger["source"]["path"],
        "source_sha256": _file_sha(source_path),
        "event_count": ledger["metrics"]["proposal_count"],
    }


def prepare(*, event_ledger_paths: list[Path], output_dir: Path) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    cases = [_case_spec(path.resolve()) for path in event_ledger_paths]
    jobs = []
    for case in cases:
        ledger = json.loads((ROOT / case["event_ledger_path"]).read_text())
        for family in FAMILIES:
            micro = build_synthesis_contract(family, event_ledger=ledger)
            jobs.append(
                {
                    "job_id": f"{case['case_id']}--{family}",
                    "case_id": case["case_id"],
                    "family": family,
                    "event_count": micro["event_count"],
                    "system_prompt_sha256": micro["system_prompt_sha256"],
                    "user_prompt_sha256": micro["user_prompt_sha256"],
                    "schema_sha256": _sha(micro["schema"]),
                    "schema_metrics": micro["schema_metrics"],
                }
            )
    contract = {
        "schema_version": CONTRACT_SCHEMA,
        "status": "frozen_before_calls",
        "phase": "C_fresh_context_synthesis",
        "date": "2026-07-11",
        "cases": cases,
        "jobs": jobs,
        "configuration": {
            "provider": "openrouter",
            "model": MODEL,
            "wire_mode": "json_object",
            "temperature": 0.0,
            "reasoning": {"enabled": False},
            "max_output_tokens": 4200,
            "provider_timeout_seconds": 120,
            "parallel_workers": 3,
            "automatic_retries": 0,
            "provider_fallbacks": False,
            "response_healing": False,
            "fresh_context_per_family": True,
            "prior_model_prose_visible": False,
            "graph_calls": 0,
            "pipeline_calls": 0,
        },
        "budget": {
            "maximum_provider_calls": len(jobs),
            "estimated_total_cost_ceiling_usd": 0.09,
        },
        "mechanical_success_requirements": {
            "operational_success_rate": 1.0,
            "typed_admission_rate": 1.0,
            "invalid_synthesis_count": 0,
            "compiled_handoff_rate": 1.0,
            "handoff_violation_count": 0,
            "direct_graph_seed_count": 0,
        },
        "semantic_review_requirements": {
            "current_position_and_ownership_preserved": True,
            "late_material_contributions_preserved": True,
            "focal_thread_trajectory_and_disposition_preserved": True,
            "constraint_source_strength_inflation_count": 0,
            "atomic_constraint_precision_min": 0.80,
            "atomic_constraint_recall_min": 0.75,
        },
        "practice_check": {
            "checked": "2026-07-11",
            "model_page": "https://openrouter.ai/google/gemini-3.1-flash-lite",
            "structured_output_docs": "https://openrouter.ai/docs/guides/features/structured-outputs",
            "design_departure": "prompted JSON remains deliberate because strict provider schema transport failed; local typed parsing remains authoritative for shape",
        },
        "artifact_locks": [
            {"path": "scripts/evals/run_conversation_event_synthesis_phase.py", "sha256": _file_sha(ROOT / "scripts/evals/run_conversation_event_synthesis_phase.py")},
            {"path": "engine/system_b/conversation_event_harvesting.py", "sha256": _file_sha(ROOT / "engine/system_b/conversation_event_harvesting.py")},
            {"path": "engine/system_b/conversation_event_pipeline.py", "sha256": _file_sha(ROOT / "engine/system_b/conversation_event_pipeline.py")},
            {"path": "docs/conversation-understanding/decomposition-design-check-2026-07-11.md", "sha256": _file_sha(ROOT / "docs/conversation-understanding/decomposition-design-check-2026-07-11.md")},
        ],
        "non_claims": [
            "mechanical_compilation_is_not_semantic_correctness",
            "development_cases_are_not_independent_product_proof",
            "phase_c_does_not_authorize_graph_or_runtime_integration",
        ],
    }
    contract_path = output_dir / "contract.json"
    _write(contract_path, contract)
    _write(
        output_dir / "authorization.json",
        {
            "schema_version": AUTHORIZATION_SCHEMA,
            "status": "authorized_under_founder_delegated_a_to_e_goal",
            "contract_path": str(contract_path.relative_to(ROOT)),
            "contract_sha256": _file_sha(contract_path),
            "maximum_provider_calls": len(jobs),
            "automatic_retries": 0,
            "graph_calls": 0,
            "pipeline_calls": 0,
        },
    )
    return contract


def validate(contract: dict[str, Any], authorization: dict[str, Any], contract_path: Path) -> None:
    if contract.get("schema_version") != CONTRACT_SCHEMA or contract.get("status") != "frozen_before_calls":
        raise ValueError("synthesis contract is not frozen")
    if authorization.get("schema_version") != AUTHORIZATION_SCHEMA or authorization.get("contract_sha256") != _file_sha(contract_path):
        raise ValueError("synthesis authorization mismatch")
    for lock in contract["artifact_locks"]:
        if _file_sha(ROOT / lock["path"]) != lock["sha256"]:
            raise ValueError(f"artifact lock drifted: {lock['path']}")
    observed = []
    for case in contract["cases"]:
        path = ROOT / case["event_ledger_path"]
        if _file_sha(path) != case["event_ledger_sha256"] or _file_sha(ROOT / case["source_path"]) != case["source_sha256"]:
            raise ValueError(f"case evidence lock drifted: {case['case_id']}")
        ledger = json.loads(path.read_text())
        for family in FAMILIES:
            micro = build_synthesis_contract(family, event_ledger=ledger)
            observed.append(
                {
                    "job_id": f"{case['case_id']}--{family}",
                    "case_id": case["case_id"],
                    "family": family,
                    "event_count": micro["event_count"],
                    "system_prompt_sha256": micro["system_prompt_sha256"],
                    "user_prompt_sha256": micro["user_prompt_sha256"],
                    "schema_sha256": _sha(micro["schema"]),
                    "schema_metrics": micro["schema_metrics"],
                }
            )
    if observed != contract["jobs"]:
        raise ValueError("synthesis jobs drifted")


def _call(job: dict[str, Any], contract: dict[str, Any], ledgers: dict[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    micro = build_synthesis_contract(job["family"], event_ledger=ledgers[job["case_id"]])
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    base = {
        "schema_version": CALL_SCHEMA,
        "job_id": job["job_id"],
        "case_id": job["case_id"],
        "family": job["family"],
        "requested_model": MODEL,
        "event_count": micro["event_count"],
        "system_prompt_sha256": micro["system_prompt_sha256"],
        "user_prompt_sha256": micro["user_prompt_sha256"],
        "schema_sha256": _sha(micro["schema"]),
    }
    if not api_key:
        return {**base, "operational_status": "missing_api_key", "provider_calls": 0}
    config = contract["configuration"]
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": micro["system_prompt"]},
            {"role": "user", "content": micro["user_prompt"]},
        ],
        "response_format": {"type": "json_object"},
        "provider": {"require_parameters": True, "allow_fallbacks": False},
        "temperature": config["temperature"],
        "max_tokens": config["max_output_tokens"],
        "reasoning": config["reasoning"],
    }
    req = request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=config["provider_timeout_seconds"]) as response:
            provider = json.loads(response.read().decode())
    except error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        return {**base, "operational_status": f"http_error_{exc.code}", "provider_error_sha256": hashlib.sha256(detail.encode()).hexdigest(), "provider_calls": 1, "duration_seconds": round(time.monotonic() - started, 3)}
    except Exception as exc:  # noqa: BLE001
        return {**base, "operational_status": "provider_error", "provider_error_type": type(exc).__name__, "provider_calls": 1, "duration_seconds": round(time.monotonic() - started, 3)}
    choices = provider.get("choices") if isinstance(provider.get("choices"), list) else []
    choice = choices[0] if choices and isinstance(choices[0], dict) else {}
    message = choice.get("message") if isinstance(choice.get("message"), dict) else {}
    content = str(message.get("content", ""))
    payload = _extract_json_object(content)
    typed, issues_raw = parse_synthesis(job["family"], payload)
    issues = [item.to_dict() for item in issues_raw]
    usage = provider.get("usage") if isinstance(provider.get("usage"), dict) else {}
    pt, ct, tt = usage.get("prompt_tokens"), usage.get("completion_tokens"), usage.get("total_tokens")
    usage_ok = all(isinstance(item, int) and item > 0 for item in (pt, ct, tt))
    served = str(provider.get("model", ""))
    attribution = _model_attribution(MODEL, served)
    operational_ok = bool(choices) and choice.get("finish_reason") != "error" and usage_ok and attribution in {"matched", "served_version_alias"}
    price = lookup_chat_price("openrouter", MODEL)
    cost = estimate_chat_cost_usd(price=price, prompt_tokens=pt, completion_tokens=ct) if price and usage_ok else None
    return {
        **base,
        "operational_status": "ok" if operational_ok else "operational_failure",
        "typed_status": "admitted" if typed is not None and not issues else "quarantined",
        "candidate_payload": payload,
        "validation_issues": issues,
        "served_model": served,
        "model_attribution_status": attribution,
        "finish_reason": choice.get("finish_reason"),
        "prompt_tokens": pt,
        "completion_tokens": ct,
        "total_tokens": tt,
        "estimated_cost_usd": cost,
        "response_sha256": hashlib.sha256(content.encode()).hexdigest(),
        "provider_payload_sha256": _sha(provider),
        "provider_calls": 1,
        "automatic_retries": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "duration_seconds": round(time.monotonic() - started, 3),
        "raw_provider_content_included": False,
    }


def execute(*, contract_path: Path, authorization_path: Path, env_file: Path, output_dir: Path) -> dict[str, Any]:
    contract_path, authorization_path, output_dir = contract_path.resolve(), authorization_path.resolve(), output_dir.resolve()
    contract, authorization = json.loads(contract_path.read_text()), json.loads(authorization_path.read_text())
    validate(contract, authorization, contract_path)
    _load_env(env_file)
    calls_dir = output_dir / "calls"
    if calls_dir.exists() and any(calls_dir.glob("*.json")):
        raise ValueError("synthesis call directory is not empty")
    ledgers = {case["case_id"]: json.loads((ROOT / case["event_ledger_path"]).read_text()) for case in contract["cases"]}
    results = []
    with ThreadPoolExecutor(max_workers=contract["configuration"]["parallel_workers"]) as pool:
        futures = {pool.submit(_call, job, contract, ledgers): job for job in contract["jobs"]}
        for future in as_completed(futures):
            result = future.result()
            _write(calls_dir / f"{result['job_id']}.json", result)
            results.append(result)
    results.sort(key=lambda row: row["job_id"])
    case_rows = []
    for case in contract["cases"]:
        case_id = case["case_id"]
        source_text = (ROOT / case["source_path"]).read_text()
        catalog = build_source_catalog(source_text=source_text, source_path=case["source_path"])
        syntheses = {}
        case_calls = [row for row in results if row["case_id"] == case_id]
        for row in case_calls:
            if row.get("typed_status") == "admitted":
                typed, issues = parse_synthesis(row["family"], row["candidate_payload"])
                if typed is not None and not issues:
                    syntheses[row["family"]] = typed
        synthesis_ledger = build_synthesis_ledger(case_id=case_id, event_ledger=ledgers[case_id], syntheses=syntheses)
        compiled, compiler = compile_handoff_from_event_ledgers(
            event_ledger=ledgers[case_id],
            synthesis_ledger=synthesis_ledger,
            catalog=catalog,
            handoff_status="model_probe_unreviewed",
        )
        violations = validate_conversation_state_handoff(compiled, source_text=source_text) if compiled else [{"code": "compiled_handoff_missing"}]
        boundary = build_fact_free_routing_boundary(compiled) if compiled and not violations else None
        case_dir = output_dir / "cases" / case_id
        _write(case_dir / "synthesis-ledger.json", synthesis_ledger)
        _write(case_dir / "compiled-handoff.json", compiled)
        _write(case_dir / "compiler-result.json", compiler)
        row = {
            "case_id": case_id,
            "expected_call_count": len(FAMILIES),
            "provider_call_count": sum(item.get("provider_calls", 0) for item in case_calls),
            "operational_success_count": sum(item.get("operational_status") == "ok" for item in case_calls),
            "typed_admission_count": sum(item.get("typed_status") == "admitted" for item in case_calls),
            "invalid_synthesis_count": synthesis_ledger["metrics"]["invalid_synthesis_count"],
            "compiled": compiled is not None and compiler["status"] == "compiled",
            "handoff_violation_count": len(violations),
            "direct_graph_seed_count": boundary["direct_graph_seed_count"] if boundary else None,
            "position_count": len(compiled["positions"]) if compiled else 0,
            "thread_count": len(compiled["threads"]) if compiled else 0,
            "constraint_count": len(compiled["constraints"]) if compiled else 0,
        }
        _write(case_dir / "result.json", {**row, "handoff_violations": violations})
        case_rows.append(row)
    expected = sum(row["expected_call_count"] for row in case_rows)
    operational = sum(row["operational_success_count"] for row in case_rows)
    admitted = sum(row["typed_admission_count"] for row in case_rows)
    mechanical_pass = (
        operational == expected
        and admitted == expected
        and all(row["invalid_synthesis_count"] == 0 and row["compiled"] and row["handoff_violation_count"] == 0 and row["direct_graph_seed_count"] == 0 for row in case_rows)
    )
    summary = {
        "schema_version": RESULT_SCHEMA,
        "status": "mechanical_pass_semantic_review_required" if mechanical_pass else "fail",
        "phase": contract["phase"],
        "case_count": len(case_rows),
        "provider_call_count": sum(row.get("provider_calls", 0) for row in results),
        "automatic_retry_count": 0,
        "operational_success_rate": round(operational / expected, 4),
        "typed_admission_rate": round(admitted / expected, 4),
        "estimated_cost_usd": round(sum(row.get("estimated_cost_usd") or 0 for row in results), 8),
        "prompt_tokens": sum(row.get("prompt_tokens") or 0 for row in results),
        "completion_tokens": sum(row.get("completion_tokens") or 0 for row in results),
        "invalid_synthesis_count": sum(row["invalid_synthesis_count"] for row in case_rows),
        "compiled_case_count": sum(row["compiled"] for row in case_rows),
        "handoff_violation_count": sum(row["handoff_violation_count"] for row in case_rows),
        "direct_graph_seed_count": sum(row["direct_graph_seed_count"] or 0 for row in case_rows),
        "cases": case_rows,
        "semantic_review_requirements": contract["semantic_review_requirements"],
        "runtime_modified": False,
        "non_claims": contract["non_claims"],
    }
    _write(output_dir / "result.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--event-ledger", action="append", type=Path, default=[])
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    if args.prepare:
        print(json.dumps(prepare(event_ledger_paths=args.event_ledger, output_dir=args.output_dir), indent=2))
        return
    if args.execute:
        if not args.contract or not args.authorization or not args.env_file:
            raise ValueError("execution requires contract, authorization, and env file")
        print(json.dumps(execute(contract_path=args.contract, authorization_path=args.authorization, env_file=args.env_file, output_dir=args.output_dir), indent=2))
        return
    raise ValueError("choose --prepare or --execute")


if __name__ == "__main__":
    main()
