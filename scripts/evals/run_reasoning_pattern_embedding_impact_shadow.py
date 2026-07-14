#!/usr/bin/env python3
"""Run one frozen batch embedding shadow over fact-free pattern fingerprints."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.activation_matcher import _to_reasoning_prose, match_activation  # noqa: E402
from engine.system_b.reasoning_pattern_activation_shadow import fingerprint_from_reasoning_pattern_packet  # noqa: E402
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402
from scripts.evals.run_reasoning_process_graph_impact_shadow import _load_explicit_graph  # noqa: E402


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _text_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_contract(contract: dict, contract_path: Path) -> dict:
    if contract.get("status") != "frozen_before_one_batch_embedding_request":
        raise RuntimeError("embedding shadow contract is not frozen")
    for item in contract["frozen_inputs"]:
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"frozen input drifted: {item['path']}")
    result = _load(ROOT / contract["deterministic_result_path"])
    full = fingerprint_from_reasoning_pattern_packet(result["arms"]["housing_source_first"]["packet"])
    ablated = fingerprint_from_reasoning_pattern_packet(result["arms"]["housing_missing_reversal_ablation"]["packet"])
    texts = [_to_reasoning_prose(full), _to_reasoning_prose(ablated)]
    if [_text_sha(text) for text in texts] != contract["input_text_sha256"]:
        raise RuntimeError("fact-free embedding text drifted")
    expected_config = {"provider": "openai", "endpoint": "https://api.openai.com/v1/embeddings", "model": "text-embedding-3-large", "encoding_format": "float", "dimensions": 3072, "maximum_http_requests": 1, "batch_input_count": 2, "automatic_retries": 0, "timeout_seconds": 30}
    if contract["call_configuration"] != expected_config:
        raise RuntimeError("embedding configuration drifted")
    return {"status": "reasoning_pattern_embedding_shadow_contract_valid", "contract_path": str(contract_path.relative_to(ROOT)), "embedding_requests_made": 0}


def _selection(graph, fingerprint, vector: list[float], seeds: list[str], db_path: Path) -> dict:
    expected_text = _to_reasoning_prose(fingerprint)
    def matcher(reasoning_input, edges, *, db_path, api_key):
        if _to_reasoning_prose(reasoning_input) != expected_text:
            raise TypeError("fingerprint text drifted during activation match")
        return match_activation(reasoning_input, edges, db_path=db_path, api_key="precomputed-shadow", embedder=lambda text, key: vector if text == expected_text else None)
    rows = []
    for seed in seeds:
        value = graph.neighborhood((seed,), max_supporting_models=2, max_risk_models=1, reasoning_context=fingerprint, embeddings_db_path=db_path, openai_api_key="precomputed-shadow", _activation_matcher=matcher)
        rows.append({"seed_model_id": seed, "supporting_model_ids": list(value.supporting_model_ids), "risk_model_ids": list(value.risk_model_ids), "tiebreaker_supporting": asdict(value.tiebreaker_supporting), "tiebreaker_risk": asdict(value.tiebreaker_risk)})
    return {"per_seed": rows, "supporting_union": sorted({item for row in rows for item in row["supporting_model_ids"]}), "risk_union": sorted({item for row in rows for item in row["risk_model_ids"]}), "tiebreaker_fired_count": sum(int(row[side]["fired"]) for row in rows for side in ("tiebreaker_supporting", "tiebreaker_risk"))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path, contract = args.contract.resolve(), _load(args.contract.resolve())
    validation = validate_contract(contract, contract_path)
    if args.dry_run:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0
    if args.env_file is None or args.output_dir is None:
        raise RuntimeError("execution arguments missing")
    output = args.output_dir.resolve()
    if not output.is_dir() or (output / "embedding-result.json").exists() or (output / "embedding-call-started.json").exists():
        raise RuntimeError("embedding output absent, complete, or already started")
    _load_env(args.env_file.resolve())
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required")
    deterministic = _load(ROOT / contract["deterministic_result_path"])
    full_fp = fingerprint_from_reasoning_pattern_packet(deterministic["arms"]["housing_source_first"]["packet"])
    ablated_fp = fingerprint_from_reasoning_pattern_packet(deterministic["arms"]["housing_missing_reversal_ablation"]["packet"])
    texts = [_to_reasoning_prose(full_fp), _to_reasoning_prose(ablated_fp)]
    _write(output / "embedding-call-started.json", {"schema_version": "lolla.reasoning_pattern_embedding_call_started.v1", "status": "embedding_request_may_have_started_do_not_rerun_if_result_missing", "started_at_utc": datetime.now(timezone.utc).isoformat(), "model": contract["call_configuration"]["model"], "input_text_sha256": contract["input_text_sha256"]})
    payload = json.dumps({"input": texts, "model": contract["call_configuration"]["model"], "encoding_format": "float", "dimensions": contract["call_configuration"]["dimensions"]}).encode("utf-8")
    request = urllib.request.Request(contract["call_configuration"]["endpoint"], data=payload, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=contract["call_configuration"]["timeout_seconds"]) as response:
        provider = json.loads(response.read().decode("utf-8"))
    vectors = [item["embedding"] for item in sorted(provider["data"], key=lambda item: item["index"])]
    if len(vectors) != 2 or any(len(vector) != 3072 for vector in vectors):
        raise RuntimeError("embedding response dimension drifted")
    graph = _load_explicit_graph(ROOT / contract["relationship_graph_path"])
    db_path = ROOT / contract["embeddings_db_path"]
    full_seeds = [item["model_id"] for item in deterministic["arms"]["housing_source_first"]["seed_route"]["seed_candidates"]]
    ablated_seeds = [item["model_id"] for item in deterministic["arms"]["housing_missing_reversal_ablation"]["seed_route"]["seed_candidates"]]
    full_selection = _selection(graph, full_fp, vectors[0], full_seeds, db_path)
    ablated_selection = _selection(graph, ablated_fp, vectors[1], ablated_seeds, db_path)
    result = {"schema_version": "lolla.reasoning_pattern_embedding_impact_shadow_result.v1", "status": "fact_free_embedding_impact_shadow_complete", "contract_path": str(contract_path.relative_to(ROOT)), "contract_sha256": _sha(contract_path), "embedding_http_requests": 1, "embedding_input_count": 2, "model": provider.get("model", ""), "vector_dimensions": [len(vector) for vector in vectors], "usage": provider.get("usage", {}), "input_text_sha256": contract["input_text_sha256"], "source_provider_full_projection_embedding_reused": True, "full_selection": full_selection, "ablation_selection": ablated_selection, "sensitivity": {"supporting_union_changed": full_selection["supporting_union"] != ablated_selection["supporting_union"], "risk_union_changed": full_selection["risk_union"] != ablated_selection["risk_union"], "full_tiebreaker_fired_count": full_selection["tiebreaker_fired_count"], "ablation_tiebreaker_fired_count": ablated_selection["tiebreaker_fired_count"]}, "boundary": {"raw_role_prose_embedded": False, "facts_embedded": False, "controlled_pattern_text_only": True, "provider_chat_calls": 0, "embedding_http_requests": 1, "evaluator_calls": 0, "reconsideration_calls": 0, "runtime_mutations": 0, "receipts_written": 0, "scalar_quality_score_computed": False, "production_integration_authorized": False}}
    _write(output / "embedding-result.json", result)
    print(json.dumps({"status": result["status"], "model": result["model"], "usage": result["usage"], "sensitivity": result["sensitivity"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
