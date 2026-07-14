#!/usr/bin/env python3
"""Build provider-free local chronological exploration artifacts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.conversation_state_candidates import build_source_catalog  # noqa: E402
from engine.system_b.reasoning_process_contracts import schema_metrics  # noqa: E402
from engine.system_b.reasoning_process_exploration_local import (  # noqa: E402
    build_case_receipt,
    build_local_prompts,
    build_local_packets,
    compile_local_response,
    local_response_schema,
    protected_local_fixture_response,
)
from engine.system_b.reasoning_process_view_specific import (  # noqa: E402
    VIEW_QUESTIONS,
    build_annotated_reader_packet,
)
from engine.system_b.reasoning_process_views import (  # noqa: E402
    canonical_json_bytes,
    sha256_bytes,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _display(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def build(
    *,
    root: Path,
    output: Path,
    allow_prior_alternative_citation: bool = False,
    contract_path: Path | None = None,
) -> dict[str, Any]:
    contract_path = contract_path or (
        root / "docs/evals/reasoning-process-exploration-local-harvester-contract-v1.json"
    )
    contract = _load(contract_path)
    if contract.get("status") not in {
        "frozen_provider_free_before_implementation",
        "frozen_provider_free_before_v2_build",
    }:
        raise RuntimeError("local exploration contract is not frozen")
    phase2 = _load(root / "docs/evals/reasoning-process-phase2-coverage-contract-v1.json")
    schema = local_response_schema()
    schema_stats = schema_metrics(schema)
    if schema_stats["bytes"] > contract["gates"]["max_provider_schema_bytes"]:
        raise RuntimeError("local exploration schema exceeds byte budget")
    if schema_stats["depth"] > contract["gates"]["max_provider_schema_depth"]:
        raise RuntimeError("local exploration schema exceeds depth budget")
    schema_path = output / "provider-schema.json"
    _write(schema_path, schema)

    case_results: list[dict[str, Any]] = []
    total_windows = 0
    total_focal_aliases = 0
    total_context_aliases = 0
    max_packet_bytes = 0
    max_user_prompt_bytes = 0
    for case in phase2["cases"]:
        case_id = case["case_id"]
        source_path = root / case["source_path"]
        source_text = source_path.read_text(encoding="utf-8")
        full_wrapper = _load(
            root
            / "research/reasoning-process-view-specific-interface-2026-07-11/cases"
            / case_id
            / "exploration_and_alternatives/reader-packet.json"
        )
        packets = build_local_packets(
            case_id=case_id,
            source_path=case["source_path"],
            source_text=source_text,
            global_alias_map=full_wrapper["evidence_alias_map"],
            allow_prior_alternative_citation=allow_prior_alternative_citation,
        )
        target = next(
            target
            for target in case["targets"]
            if target["view_kind"] == "exploration_and_alternatives"
        )
        target_turns = {item["turn_index"] for item in target["source_evidence"]}
        if len(target_turns) != 1:
            raise RuntimeError("protected exploration relationship crosses focal pairs")
        target_turn = next(iter(target_turns))
        focal_wrapper = next(
            wrapper
            for wrapper in packets
            if wrapper["packet"]["focal_turn_index"] == target_turn
        )
        catalog = build_source_catalog(
            source_text=source_text, source_path=case["source_path"]
        )
        response = protected_local_fixture_response(
            target=target, wrapper=focal_wrapper, catalog=catalog
        )
        compiled = compile_local_response(
            response=response,
            wrapper=focal_wrapper,
            producer_kind="source_reviewer",
            producer_id="exploration-local-same-session-nonblind",
            record_identity=target["target_id"],
        )
        receipt = build_case_receipt(
            case_id=case_id,
            source_path=case["source_path"],
            source_text=source_text,
            packets=packets,
            protected_compilation=compiled,
        )
        case_dir = output / "cases" / case_id
        packet_artifacts = []
        for wrapper in packets:
            turn_index = wrapper["packet"]["focal_turn_index"]
            path = case_dir / "windows" / f"turn-{turn_index:03d}.json"
            prompts = build_local_prompts(wrapper)
            prompt_path = case_dir / "prompt-manifests" / f"turn-{turn_index:03d}.json"
            _write(path, wrapper)
            _write(
                prompt_path,
                {
                    "system_prompt": prompts["system_prompt"],
                    "system_prompt_sha256": prompts["system_prompt_sha256"],
                    "user_prompt_sha256": prompts["user_prompt_sha256"],
                    "user_prompt_utf8_bytes": len(prompts["user_prompt"].encode("utf-8")),
                    "target_blind": True,
                    "provider_call_authorized": False,
                },
            )
            packet_artifacts.append(
                {
                    "focal_turn_index": turn_index,
                    "path": _display(path, root),
                    "input_utf8_bytes": wrapper["metrics"]["input_utf8_bytes"],
                    "focal_sentence_count": wrapper["metrics"]["focal_sentence_count"],
                    "context_sentence_count": wrapper["metrics"]["context_sentence_count"],
                    "prompt_manifest_path": _display(prompt_path, root),
                }
            )
            total_focal_aliases += wrapper["metrics"]["focal_sentence_count"]
            total_context_aliases += wrapper["metrics"]["context_sentence_count"]
            max_packet_bytes = max(
                max_packet_bytes, wrapper["metrics"]["input_utf8_bytes"]
            )
            max_user_prompt_bytes = max(
                max_user_prompt_bytes, len(prompts["user_prompt"].encode("utf-8"))
            )
        fixture_path = case_dir / "protected-fixture.json"
        receipt_path = case_dir / "case-receipt.json"
        _write(
            fixture_path,
            {
                "target_id": target["target_id"],
                "target_turn_index": target_turn,
                "response": response,
                "compiled": compiled,
                "boundary": {
                    "independent_gold": False,
                    "provider_calls": 0,
                    "semantic_exhaustiveness_validated": False,
                },
            },
        )
        _write(receipt_path, receipt)
        total_windows += len(packets)
        case_results.append(
            {
                "case_id": case_id,
                "window_count": len(packets),
                "future_max_provider_calls": len(packets),
                "future_max_records": len(packets) * 2,
                "protected_target_id": target["target_id"],
                "protected_focal_turn_index": target_turn,
                "protected_role_source_span_ids": compiled["observations"][0][
                    "role_source_span_ids"
                ],
                "protected_fixture_path": _display(fixture_path, root),
                "receipt_path": _display(receipt_path, root),
                "window_artifacts": packet_artifacts,
            }
        )

    stress_spec = contract["stress_fixture"]
    stress_source = (root / stress_spec["path"]).read_text(encoding="utf-8")
    stress_full = build_annotated_reader_packet(
        case_id="exploration-local-stress",
        view_kind="exploration_and_alternatives",
        question=VIEW_QUESTIONS["exploration_and_alternatives"],
        source_path=stress_spec["path"],
        source_text=stress_source,
        base_observations=[],
    )
    stress_packets = build_local_packets(
        case_id="exploration-local-stress",
        source_path=stress_spec["path"],
        source_text=stress_source,
        global_alias_map=stress_full["evidence_alias_map"],
        allow_prior_alternative_citation=allow_prior_alternative_citation,
    )
    stress_dir = output / "stress"
    for wrapper in stress_packets:
        _write(
            stress_dir
            / f"turn-{wrapper['packet']['focal_turn_index']:03d}.json",
            wrapper,
        )
    stress_max_bytes = max(item["metrics"]["input_utf8_bytes"] for item in stress_packets)
    stress_focal_aliases = sum(
        item["metrics"]["focal_sentence_count"] for item in stress_packets
    )
    if total_windows != contract["gates"]["expected_turn_pair_window_count"]:
        raise RuntimeError("local development window count drifted")
    if len(stress_packets) != stress_spec["expected_turn_pair_window_count"]:
        raise RuntimeError("local stress window count drifted")
    if max(max_packet_bytes, stress_max_bytes) > contract["gates"][
        "max_window_input_utf8_bytes"
    ]:
        raise RuntimeError("local window byte budget exceeded")
    report = {
        "schema_version": (
            "lolla.reasoning_process_exploration_local_report.v2"
            if allow_prior_alternative_citation
            else "lolla.reasoning_process_exploration_local_report.v1"
        ),
        "status": (
            "provider_free_local_exploration_v2_representation_pass"
            if allow_prior_alternative_citation
            else "provider_free_local_exploration_representation_pass"
        ),
        "date": contract["date"],
        "contract_path": _display(contract_path, root),
        "contract_sha256": sha256_bytes(canonical_json_bytes(contract)),
        "provider_schema": {
            "path": _display(schema_path, root),
            "metrics": schema_stats,
            "sha256": sha256_bytes(canonical_json_bytes(schema)),
        },
        "summary": {
            "case_count": len(case_results),
            "window_count": total_windows,
            "protected_fixture_count": len(case_results),
            "protected_fixture_pass_count": len(case_results),
            "focal_source_alias_count": total_focal_aliases,
            "read_only_context_alias_count": total_context_aliases,
            "max_window_input_utf8_bytes": max_packet_bytes,
            "max_user_prompt_utf8_bytes": max_user_prompt_bytes,
            "future_max_calls_per_case": max(
                item["future_max_provider_calls"] for item in case_results
            ),
            "future_max_records_per_case": max(
                item["future_max_records"] for item in case_results
            ),
            "stress_message_count": stress_full["metrics"]["source_message_count"],
            "stress_window_count": len(stress_packets),
            "stress_focal_source_alias_count": stress_focal_aliases,
            "stress_max_window_input_utf8_bytes": stress_max_bytes,
            "provider_calls": 0,
            "embedding_calls": 0,
            "evaluator_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
            "prior_context_alternative_citation_enabled": allow_prior_alternative_citation,
        },
        "cases": case_results,
        "stress": {
            "source_path": stress_spec["path"],
            "window_count": len(stress_packets),
            "focal_aliases_partition_source": True,
            "max_input_utf8_bytes": stress_max_bytes,
        },
        "decision": {
            "provider_free_representation_gate": "pass",
            "semantic_model_behavior_validated": False,
            "next_required_gate": "cold-reader and adversarial local-harvester review before any provider call",
            "phase4_transfer_authorized": False,
        },
        "nonclaims": [
            "Protected fixtures are same-session representation checks, not independent or exhaustive gold.",
            "Seven future calls per fourteen-message case is a measured upper bound, not yet an authorized runtime design.",
            "No model recall, semantic precision, final-answer quality, graph value, or runtime readiness was tested."
        ],
    }
    _write(output / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/reasoning-process-exploration-local-2026-07-11"),
    )
    parser.add_argument("--allow-prior-alternative-citation", action="store_true")
    parser.add_argument("--contract", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    report = build(
        root=root,
        output=root / args.output,
        allow_prior_alternative_citation=args.allow_prior_alternative_citation,
        contract_path=(root / args.contract if args.contract else None),
    )
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
