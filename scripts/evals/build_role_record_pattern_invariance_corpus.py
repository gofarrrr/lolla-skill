#!/usr/bin/env python3
"""Build six provider-free role-record pattern interpretation packets."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_pattern_role_record_interpreter import (  # noqa: E402
    ROLE_ORDER, build_role_record_pattern_input, build_role_record_pattern_prompts,
    role_record_pattern_response_schema,
)
from engine.system_b.reasoning_process_contracts import schema_metrics  # noqa: E402
from engine.system_b.reasoning_process_position_role_first_v241 import compile_position_current_qualification_response_v241  # noqa: E402
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _ordered(mapping: dict) -> list[dict]:
    return [mapping[role]["observations"][0] for role in ROLE_ORDER]


def _refs(*paths: str) -> list[dict[str, str]]:
    return [{"path": path, "sha256": _sha(ROOT / path)} for path in paths]


def _ablate(records: list[dict], *, arm_id: str) -> list[dict]:
    result = copy.deepcopy(records)
    qualification = result[2]
    alias = qualification["source_evidence_ids"][0]
    qualification["role_record_id"] = f"{qualification['role_record_id']}-{arm_id}"
    qualification["observation_id"] = qualification["role_record_id"]
    qualification["role_interpretation"] = "A material unresolved counterpressure remains outside the adopted current safeguards."
    qualification["source_evidence_ids"] = [alias]
    qualification["source_evidence"] = []
    qualification["stance_components"] = [{"role": "qualification", "source_evidence_id": alias, "stance_expression_kind": "uncertain_or_undecided", "stance_object_interpretation": "A material unresolved counterpressure remains outside the adopted safeguards.", "stance_object_kind": "belief_or_assessment"}]
    qualification["fidelity_note"] = "Synthetic sensitivity control retaining unresolved counterpressure while removing reversal and path-dependence meaning."
    qualification["limitations"] = "Counterfactual semantic ablation; not a source claim."
    return result


def build(output: Path) -> dict:
    registry_root = ROOT / "research/reasoning-process-position-role-first-v24-new-case-2026-07-12"
    housing_root = ROOT / "research/reasoning-process-position-role-first-v241-new-case-2026-07-12"
    registry_source = _ordered(_load(registry_root / "compiled-source-review-target.json")["role_compiled"])
    housing_source = _ordered(_load(housing_root / "compiled-source-review-target.json")["role_compiled"])

    registry_start_call = _load(ROOT / "research/reasoning-process-position-role-first-v24-probe-2026-07-12/call-01-result.json")
    registry_pair_call = _load(ROOT / "research/reasoning-process-position-role-first-v24-probe-2026-07-12/call-02-result.json")
    registry_wrapper = _load(registry_root / "position-endpoint.json")
    pair_candidate = copy.deepcopy(registry_pair_call["candidate_payload"])
    pair_candidate.pop("current_status")
    pair_candidate.pop("qualification_status")
    registry_pair = compile_position_current_qualification_response_v241(response=pair_candidate, wrapper=registry_wrapper, producer_kind="preserved_provider_replay", producer_id="deepseek/deepseek-v4-flash")
    registry_provider = [registry_start_call["compiled"]["observations"][0], registry_pair["role_compiled"]["current"]["observations"][0], registry_pair["role_compiled"]["qualification"]["observations"][0]]

    housing_result = _load(ROOT / "research/reasoning-process-position-role-first-v241-probe-2026-07-12/result.json")
    housing_roles = housing_result["joined"]["records"][0]["role_observations"]
    housing_provider = [housing_roles[role] for role in ROLE_ORDER]

    arms = [
        ("registry_source_first", "amb3-case05-registry-pharma-partnership", registry_source, _refs("research/reasoning-process-position-role-first-v24-new-case-2026-07-12/compiled-source-review-target.json"), None),
        ("registry_provider", "amb3-case05-registry-pharma-partnership", registry_provider, _refs("research/reasoning-process-position-role-first-v24-probe-2026-07-12/call-01-result.json", "research/reasoning-process-position-role-first-v24-probe-2026-07-12/call-02-result.json"), None),
        ("registry_reversal_ablation", "amb3-case05-registry-pharma-partnership", _ablate(registry_source, arm_id="registry-ablation"), _refs("research/reasoning-process-position-role-first-v24-new-case-2026-07-12/compiled-source-review-target.json"), {"active": True, "kind": "remove_reversal_and_path_dependence_meaning", "note": "Preserves generic unresolved counterpressure as a synthetic sensitivity control."}),
        ("housing_source_first", "amb3-case06-housing-retrofit-partnership", housing_source, _refs("research/reasoning-process-position-role-first-v241-new-case-2026-07-12/compiled-source-review-target.json"), None),
        ("housing_provider", "amb3-case06-housing-retrofit-partnership", housing_provider, _refs("research/reasoning-process-position-role-first-v241-probe-2026-07-12/result.json"), None),
        ("housing_reversal_ablation", "amb3-case06-housing-retrofit-partnership", _ablate(housing_source, arm_id="housing-ablation"), _refs("research/reasoning-process-position-role-first-v241-new-case-2026-07-12/compiled-source-review-target.json"), {"active": True, "kind": "remove_reversal_and_path_dependence_meaning", "note": "Preserves generic unresolved counterpressure as a synthetic sensitivity control."}),
    ]
    artifacts, max_prompt = [], 0
    schema = role_record_pattern_response_schema()
    for arm_id, case_id, records, refs, ablation in arms:
        packet = build_role_record_pattern_input(case_id=case_id, arm_id=arm_id, records=records, source_refs=refs, ablation=ablation)
        prompts = build_role_record_pattern_prompts(packet)
        max_prompt = max(max_prompt, len(prompts["user_prompt"].encode("utf-8")))
        packet_path = output / "packets" / f"{arm_id}.json"
        _write(packet_path, packet)
        artifacts.append({"arm_id": arm_id, "case_id": case_id, "packet_path": str(packet_path.relative_to(ROOT)), "packet_sha256": _sha(packet_path), "system_prompt_sha256": prompts["system_prompt_sha256"], "user_prompt_sha256": prompts["user_prompt_sha256"], "response_schema_sha256": sha256_bytes(canonical_json_bytes(schema)), "ablation_active": packet["ablation"]["active"]})
    metrics = schema_metrics(schema)
    gate = len(artifacts) == 6 and max_prompt <= 9000 and metrics["bytes"] <= 1800 and metrics["depth"] <= 8
    report = {"schema_version": "lolla.role_record_pattern_invariance_corpus.v1", "status": "provider_free_role_record_pattern_corpus_pass" if gate else "provider_free_role_record_pattern_corpus_fail", "date": "2026-07-12", "artifacts": artifacts, "summary": {"packet_count": len(artifacts), "source_first_count": 2, "provider_count": 2, "ablation_count": 2, "maximum_user_prompt_utf8_bytes": max_prompt, "response_schema_metrics": metrics, "maximum_generation_calls": 6, "provider_calls": 0, "evaluator_calls": 0, "embedding_calls": 0, "graph_calls": 0, "runtime_calls": 0}, "boundary": {"raw_conversation_in_packets": False, "source_evidence_text_in_packets": False, "role_semantic_prose_in_packets": True, "expected_patterns_in_packets": False, "deterministic_semantic_mapping": False, "production_integration_authorized": False}}
    _write(output / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.output.resolve())
    print(json.dumps({"status": report["status"], "summary": report["summary"]}, indent=2))
    return 0 if report["status"].endswith("_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
