#!/usr/bin/env python3
"""Freeze and run bounded small-window conversation event harvesting."""
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
    FAMILIES,
    build_harvest_contract,
    build_turn_pair_windows,
    parse_harvest,
)
from engine.system_b.conversation_event_pipeline import (  # noqa: E402
    build_event_ledger,
    reviewed_event_projection,
)
from engine.system_b.conversation_state_candidates import build_source_catalog  # noqa: E402
from engine.system_b.pricing import (  # noqa: E402
    PRICES_LAST_VERIFIED,
    estimate_chat_cost_usd,
    lookup_chat_price,
)
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402
from scripts.evals.run_fixed_safe_holdout_pool import (  # noqa: E402
    _extract_json_object,
    _model_attribution,
)


CONTRACT_SCHEMA = "lolla.conversation_event_harvest_contract.v1"
AUTHORIZATION_SCHEMA = "lolla.conversation_event_harvest_authorization.v1"
CALL_SCHEMA = "lolla.conversation_event_harvest_call.v1"
RESULT_SCHEMA = "lolla.conversation_event_harvest_phase_result.v1"
CASES_DIR = ROOT / "research/conversation-state-handoff-v1-2026-07-10/cases"
MIGRATION = ROOT / "research/conversation-state-recovery-v1-2026-07-11/atomic-migration.json"
MODEL = "google/gemini-3.1-flash-lite"


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def _case_paths(case_ids: list[str]) -> list[Path]:
    by_id = {}
    for path in CASES_DIR.glob("*.json"):
        payload = json.loads(path.read_text())
        by_id[payload["case_id"]] = path
    missing = sorted(set(case_ids) - set(by_id))
    if missing:
        raise ValueError(f"unknown cases: {missing}")
    return [by_id[case_id] for case_id in case_ids]


def prepare(*, case_ids: list[str], output_dir: Path, stage: str) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    jobs: list[dict[str, Any]] = []
    cases: list[dict[str, Any]] = []
    for case_path in _case_paths(case_ids):
        packet = json.loads(case_path.read_text())
        source_path = ROOT / packet["source"]["path"]
        source_text = source_path.read_text()
        catalog = build_source_catalog(
            source_text=source_text, source_path=packet["source"]["path"]
        )
        windows = build_turn_pair_windows(catalog)
        cases.append(
            {
                "case_id": packet["case_id"],
                "reviewed_packet_path": str(case_path.relative_to(ROOT)),
                "reviewed_packet_sha256": _file_sha(case_path),
                "source_path": packet["source"]["path"],
                "source_sha256": _file_sha(source_path),
                "window_count": len(windows),
            }
        )
        for window in windows:
            for family in FAMILIES:
                micro = build_harvest_contract(family, window=window)
                jobs.append(
                    {
                        "job_id": f"{packet['case_id']}--{window.window_id}--{family}",
                        "case_id": packet["case_id"],
                        "window_id": window.window_id,
                        "family": family,
                        "system_prompt_sha256": micro["system_prompt_sha256"],
                        "user_prompt_sha256": micro["user_prompt_sha256"],
                        "schema_sha256": _sha(micro["schema"]),
                        "schema_metrics": micro["schema_metrics"],
                        "allowed_span_id_count": len(window.span_ids),
                    }
                )
    maximum_calls = len(jobs)
    contract = {
        "schema_version": CONTRACT_SCHEMA,
        "status": "frozen_before_calls",
        "stage": stage,
        "date": "2026-07-11",
        "terminal_question": "Can narrow turn-pair harvesters recover reviewed local events with high recall and bounded noise?",
        "cases": cases,
        "jobs": jobs,
        "configuration": {
            "provider": "openrouter",
            "model": MODEL,
            "wire_mode": "json_object",
            "typed_schema_in_prompt": True,
            "local_typed_validation": True,
            "temperature": 0.0,
            "reasoning": {"enabled": False},
            "max_output_tokens": 900,
            "provider_timeout_seconds": 90,
            "parallel_workers": 6,
            "automatic_retries": 0,
            "provider_fallbacks": False,
            "response_healing": False,
            "evaluator_calls": 0,
            "pipeline_calls": 0,
            "graph_calls": 0,
        },
        "budget": {
            "maximum_provider_calls": maximum_calls,
            "estimated_total_cost_ceiling_usd": round(maximum_calls * 0.002, 3),
            "pricing_table_version": PRICES_LAST_VERIFIED,
        },
        "success_requirements": {
            "operational_success_rate": 1.0,
            "typed_admission_rate": 1.0,
            "invalid_source_event_count": 0,
            "cross_lens_reviewed_source_coverage_min": 0.95,
            "constraint_source_recall_min": 0.80,
            "event_count_per_case_max": 120,
            "constraint_atomicity_requires_source_review": True,
        },
        "stop_rules": {
            "no_retry": True,
            "no_prompt_change_inside_stage": True,
            "one_generic_repair_stage_maximum": True,
            "no_synthesis_or_graph_calls": True,
        },
        "composition_boundary": {
            "harvest_families_are_complementary_lenses": True,
            "position_and_thread_synthesis_can_reference_all_preserved_events": True,
            "constraint_source_strength_uses_constraint_claim_events_only": True,
            "deterministic_cross_family_relevance_gating": False,
        },
        "practice_check": {
            "checked": "2026-07-11",
            "provider_model_page": "https://openrouter.ai/google/gemini-3.1-flash-lite",
            "structured_output_docs": "https://openrouter.ai/docs/guides/features/structured-outputs",
            "verified_input_price_per_million_usd": 0.25,
            "verified_output_price_per_million_usd": 1.50,
            "deliberate_mode": "json_object plus local typed validation because strict schema transport previously failed",
        },
        "artifact_locks": [
            {"path": "scripts/evals/run_conversation_event_harvest_phase.py", "sha256": _file_sha(ROOT / "scripts/evals/run_conversation_event_harvest_phase.py")},
            {"path": "engine/system_b/conversation_event_harvesting.py", "sha256": _file_sha(ROOT / "engine/system_b/conversation_event_harvesting.py")},
            {"path": "engine/system_b/conversation_event_pipeline.py", "sha256": _file_sha(ROOT / "engine/system_b/conversation_event_pipeline.py")},
            {"path": str(MIGRATION.relative_to(ROOT)), "sha256": _file_sha(MIGRATION)},
            {"path": "docs/conversation-understanding/decomposition-design-check-2026-07-11.md", "sha256": _file_sha(ROOT / "docs/conversation-understanding/decomposition-design-check-2026-07-11.md")},
        ],
        "non_claims": [
            "development_cases_are_not_independent_product_proof",
            "source_matching_is_not_full_semantic_correctness",
            "harvesting_does_not_authorize_synthesis_or_graph_integration",
        ],
    }
    contract_path = output_dir / "contract.json"
    _write(contract_path, contract)
    authorization = {
        "schema_version": AUTHORIZATION_SCHEMA,
        "status": "authorized_under_founder_delegated_a_to_e_goal",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": _file_sha(contract_path),
        "maximum_provider_calls": maximum_calls,
        "automatic_retries": 0,
        "evaluator_calls": 0,
        "pipeline_calls": 0,
        "graph_calls": 0,
    }
    _write(output_dir / "authorization.json", authorization)
    return contract


def _load_case(case: dict[str, Any]):
    source_text = (ROOT / case["source_path"]).read_text()
    catalog = build_source_catalog(source_text=source_text, source_path=case["source_path"])
    return source_text, catalog, build_turn_pair_windows(catalog)


def validate(contract: dict[str, Any], authorization: dict[str, Any], *, contract_path: Path) -> None:
    if contract.get("schema_version") != CONTRACT_SCHEMA or contract.get("status") != "frozen_before_calls":
        raise ValueError("harvest contract is not frozen")
    if authorization.get("schema_version") != AUTHORIZATION_SCHEMA:
        raise ValueError("authorization schema invalid")
    if authorization.get("contract_sha256") != _file_sha(contract_path):
        raise ValueError("authorization does not match frozen contract")
    if authorization.get("maximum_provider_calls") != len(contract["jobs"]):
        raise ValueError("authorization call count drifted")
    for lock in contract["artifact_locks"]:
        if _file_sha(ROOT / lock["path"]) != lock["sha256"]:
            raise ValueError(f"artifact lock drifted: {lock['path']}")
    observed_jobs = []
    for case in contract["cases"]:
        if _file_sha(ROOT / case["source_path"]) != case["source_sha256"]:
            raise ValueError("source lock drifted")
        if _file_sha(ROOT / case["reviewed_packet_path"]) != case["reviewed_packet_sha256"]:
            raise ValueError("review lock drifted")
        _source_text, _catalog, windows = _load_case(case)
        for window in windows:
            for family in FAMILIES:
                micro = build_harvest_contract(family, window=window)
                observed_jobs.append(
                    {
                        "job_id": f"{case['case_id']}--{window.window_id}--{family}",
                        "case_id": case["case_id"],
                        "window_id": window.window_id,
                        "family": family,
                        "system_prompt_sha256": micro["system_prompt_sha256"],
                        "user_prompt_sha256": micro["user_prompt_sha256"],
                        "schema_sha256": _sha(micro["schema"]),
                        "schema_metrics": micro["schema_metrics"],
                        "allowed_span_id_count": len(window.span_ids),
                    }
                )
    if observed_jobs != contract["jobs"]:
        raise ValueError("frozen harvest jobs drifted")


def _call(job: dict[str, Any], contract: dict[str, Any], case_map: dict[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    _source_text, _catalog, windows = case_map[job["case_id"]]
    window = next(item for item in windows if item.window_id == job["window_id"])
    micro = build_harvest_contract(job["family"], window=window)
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    base = {
        "schema_version": CALL_SCHEMA,
        "job_id": job["job_id"],
        "case_id": job["case_id"],
        "window_id": job["window_id"],
        "family": job["family"],
        "requested_model": MODEL,
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
        return {
            **base,
            "operational_status": f"http_error_{exc.code}",
            "provider_error_sha256": hashlib.sha256(detail.encode()).hexdigest(),
            "provider_calls": 1,
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            **base,
            "operational_status": "provider_error",
            "provider_error_type": type(exc).__name__,
            "provider_calls": 1,
            "duration_seconds": round(time.monotonic() - started, 3),
        }
    choices = provider.get("choices") if isinstance(provider.get("choices"), list) else []
    choice = choices[0] if choices and isinstance(choices[0], dict) else {}
    message = choice.get("message") if isinstance(choice.get("message"), dict) else {}
    content = str(message.get("content", ""))
    payload = _extract_json_object(content)
    typed, parse_issues = parse_harvest(job["family"], payload)
    issues = [item.to_dict() for item in parse_issues]
    usage = provider.get("usage") if isinstance(provider.get("usage"), dict) else {}
    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    total_tokens = usage.get("total_tokens")
    usage_ok = all(isinstance(item, int) and item > 0 for item in (prompt_tokens, completion_tokens, total_tokens))
    served = str(provider.get("model", ""))
    attribution = _model_attribution(MODEL, served)
    operational_ok = bool(choices) and choice.get("finish_reason") != "error" and usage_ok and attribution in {"matched", "served_version_alias"}
    price = lookup_chat_price("openrouter", MODEL)
    cost = estimate_chat_cost_usd(price=price, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens) if price and usage_ok else None
    return {
        **base,
        "operational_status": "ok" if operational_ok else "operational_failure",
        "typed_status": "admitted" if typed is not None and not issues else "quarantined",
        "candidate_payload": payload,
        "validation_issues": issues,
        "served_model": served,
        "model_attribution_status": attribution,
        "finish_reason": choice.get("finish_reason"),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": cost,
        "response_sha256": hashlib.sha256(content.encode()).hexdigest(),
        "provider_payload_sha256": _sha(provider),
        "provider_calls": 1,
        "automatic_retries": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "evaluator_calls": 0,
        "duration_seconds": round(time.monotonic() - started, 3),
        "raw_provider_content_included": False,
    }


def _source_overlap(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if left["speaker"] != right["speaker"] or left["turn_index"] != right["turn_index"]:
        return False
    return left["text"] in right["text"] or right["text"] in left["text"]


def _event_matches(family: str, gold: dict[str, Any], predicted: dict[str, Any]) -> bool:
    gold_sources = gold["event_snapshot"]["resolved_source"]
    pred_sources = predicted["event_snapshot"]["resolved_source"]
    if not any(_source_overlap(a, b) for a in gold_sources for b in pred_sources):
        return False
    return True


def _family_score(family: str, gold: dict[str, Any], predicted: dict[str, Any]) -> dict[str, Any]:
    gold_rows = [row for row in gold["events"] if row["family"] == family and row["synthesis_eligible"]]
    pred_rows = [row for row in predicted["events"] if row["family"] == family and row["synthesis_eligible"]]
    unused = set(range(len(pred_rows)))
    matches = []
    for gold_index, gold_row in enumerate(gold_rows):
        match = next((index for index in sorted(unused) if _event_matches(family, gold_row, pred_rows[index])), None)
        if match is not None:
            unused.remove(match)
            matches.append({"gold_event_id": gold_row["event_id"], "predicted_event_id": pred_rows[match]["event_id"]})
    matched = len(matches)
    return {
        "family": family,
        "reviewed_event_count": len(gold_rows),
        "predicted_event_count": len(pred_rows),
        "matched_event_count": matched,
        "precision": round(matched / len(pred_rows), 4) if pred_rows else (1.0 if not gold_rows else 0.0),
        "recall": round(matched / len(gold_rows), 4) if gold_rows else 1.0,
        "matches": matches,
        "semantic_text_review_required": family == "constraint_claims",
    }


def _cross_lens_coverage(gold: dict[str, Any], predicted: dict[str, Any]) -> dict[str, Any]:
    gold_rows = [row for row in gold["events"] if row["synthesis_eligible"]]
    predicted_rows = [row for row in predicted["events"] if row["synthesis_eligible"]]
    covered = []
    for gold_row in gold_rows:
        gold_sources = gold_row["event_snapshot"]["resolved_source"]
        if any(
            _source_overlap(gold_source, predicted_source)
            for predicted_row in predicted_rows
            for predicted_source in predicted_row["event_snapshot"]["resolved_source"]
            for gold_source in gold_sources
        ):
            covered.append(gold_row["event_id"])
    return {
        "reviewed_event_count": len(gold_rows),
        "covered_reviewed_event_count": len(covered),
        "coverage": round(len(covered) / len(gold_rows), 4) if gold_rows else 1.0,
        "covered_event_ids": covered,
    }


def execute(*, contract_path: Path, authorization_path: Path, env_file: Path, output_dir: Path) -> dict[str, Any]:
    contract_path = contract_path.resolve()
    authorization_path = authorization_path.resolve()
    output_dir = output_dir.resolve()
    contract = json.loads(contract_path.read_text())
    authorization = json.loads(authorization_path.read_text())
    validate(contract, authorization, contract_path=contract_path)
    _load_env(env_file)
    calls_dir = output_dir / "calls"
    if calls_dir.exists() and any(calls_dir.glob("*.json")):
        raise ValueError("call output directory is not empty; refusing to overwrite evidence")
    case_map = {case["case_id"]: _load_case(case) for case in contract["cases"]}
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=contract["configuration"]["parallel_workers"]) as pool:
        future_map = {pool.submit(_call, job, contract, case_map): job for job in contract["jobs"]}
        for future in as_completed(future_map):
            result = future.result()
            _write(calls_dir / f"{result['job_id']}.json", result)
            results.append(result)
    results.sort(key=lambda row: row["job_id"])
    migration = json.loads(MIGRATION.read_text())
    case_rows = []
    for case in contract["cases"]:
        source_text, catalog, windows = case_map[case["case_id"]]
        packet = json.loads((ROOT / case["reviewed_packet_path"]).read_text())
        reviewed_harvests, _projection = reviewed_event_projection(
            packet=packet, catalog=catalog, windows=windows, atomic_migrations=migration
        )
        gold = build_event_ledger(
            case_id=case["case_id"], catalog=catalog, windows=windows, harvests=reviewed_harvests
        )
        harvests = {}
        case_calls = [row for row in results if row["case_id"] == case["case_id"]]
        for row in case_calls:
            if row.get("typed_status") == "admitted":
                typed, issues = parse_harvest(row["family"], row["candidate_payload"])
                if typed is not None and not issues:
                    harvests[(row["family"], row["window_id"])] = typed
        predicted = build_event_ledger(
            case_id=case["case_id"], catalog=catalog, windows=windows, harvests=harvests
        )
        scores = {family: _family_score(family, gold, predicted) for family in FAMILIES}
        cross_lens = _cross_lens_coverage(gold, predicted)
        _write(output_dir / "cases" / case["case_id"] / "predicted-event-ledger.json", predicted)
        _write(output_dir / "cases" / case["case_id"] / "reviewed-event-ledger.json", gold)
        row = {
            "case_id": case["case_id"],
            "provider_call_count": sum(item["provider_calls"] for item in case_calls),
            "operational_success_count": sum(item.get("operational_status") == "ok" for item in case_calls),
            "typed_admission_count": sum(item.get("typed_status") == "admitted" for item in case_calls),
            "expected_call_count": len(windows) * len(FAMILIES),
            "invalid_source_event_count": predicted["metrics"]["invalid_event_count"],
            "missing_harvest_count": predicted["metrics"]["missing_harvest_count"],
            "proposal_count": predicted["metrics"]["proposal_count"],
            "reviewed_event_count": gold["metrics"]["proposal_count"],
            "proposal_to_reviewed_event_ratio": round(predicted["metrics"]["proposal_count"] / gold["metrics"]["proposal_count"], 4),
            "scores": scores,
            "cross_lens_source_coverage": cross_lens,
        }
        _write(output_dir / "cases" / case["case_id"] / "result.json", row)
        case_rows.append(row)
    thresholds = contract["success_requirements"]
    totals = {}
    for family in FAMILIES:
        reviewed = sum(row["scores"][family]["reviewed_event_count"] for row in case_rows)
        predicted = sum(row["scores"][family]["predicted_event_count"] for row in case_rows)
        matched = sum(row["scores"][family]["matched_event_count"] for row in case_rows)
        totals[family] = {
            "reviewed_event_count": reviewed,
            "predicted_event_count": predicted,
            "matched_event_count": matched,
            "precision": round(matched / predicted, 4) if predicted else 0.0,
            "recall": round(matched / reviewed, 4) if reviewed else 1.0,
        }
    operational = sum(row["operational_success_count"] for row in case_rows)
    admitted = sum(row["typed_admission_count"] for row in case_rows)
    expected = sum(row["expected_call_count"] for row in case_rows)
    cross_lens_reviewed = sum(row["cross_lens_source_coverage"]["reviewed_event_count"] for row in case_rows)
    cross_lens_covered = sum(row["cross_lens_source_coverage"]["covered_reviewed_event_count"] for row in case_rows)
    cross_lens_coverage = round(cross_lens_covered / cross_lens_reviewed, 4) if cross_lens_reviewed else 1.0
    passes = (
        operational == expected
        and admitted == expected
        and sum(row["invalid_source_event_count"] for row in case_rows) == 0
        and cross_lens_coverage >= thresholds["cross_lens_reviewed_source_coverage_min"]
        and totals["constraint_claims"]["recall"] >= thresholds["constraint_source_recall_min"]
        and all(row["proposal_count"] <= thresholds["event_count_per_case_max"] for row in case_rows)
    )
    summary = {
        "schema_version": RESULT_SCHEMA,
        "status": "mechanical_pass_semantic_text_review_pending" if passes else "fail",
        "stage": contract["stage"],
        "case_count": len(case_rows),
        "provider_call_count": sum(row.get("provider_calls", 0) for row in results),
        "automatic_retry_count": 0,
        "operational_success_rate": round(operational / expected, 4),
        "typed_admission_rate": round(admitted / expected, 4),
        "estimated_cost_usd": round(sum(row.get("estimated_cost_usd") or 0 for row in results), 8),
        "prompt_tokens": sum(row.get("prompt_tokens") or 0 for row in results),
        "completion_tokens": sum(row.get("completion_tokens") or 0 for row in results),
        "invalid_source_event_count": sum(row["invalid_source_event_count"] for row in case_rows),
        "family_totals": totals,
        "cross_lens_source_coverage": {
            "reviewed_event_count": cross_lens_reviewed,
            "covered_reviewed_event_count": cross_lens_covered,
            "coverage": cross_lens_coverage,
        },
        "cases": case_rows,
        "provider_calls_outside_harvest": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_modified": False,
        "non_claims": contract["non_claims"],
    }
    _write(output_dir / "result.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--stage", default="B1_harvest_baseline")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    if args.prepare:
        print(json.dumps(prepare(case_ids=args.case_id, output_dir=args.output_dir, stage=args.stage), indent=2))
        return
    if args.execute:
        if not args.contract or not args.authorization or not args.env_file:
            raise ValueError("execution requires --contract, --authorization, and --env-file")
        print(json.dumps(execute(contract_path=args.contract, authorization_path=args.authorization, env_file=args.env_file, output_dir=args.output_dir), indent=2))
        return
    raise ValueError("choose --prepare or --execute")


if __name__ == "__main__":
    main()
