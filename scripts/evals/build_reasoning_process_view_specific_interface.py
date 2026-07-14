#!/usr/bin/env python3
"""Build and verify the provider-free view-specific interface redesign."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.conversation_state_candidates import (  # noqa: E402
    build_source_catalog,
)
from engine.system_b.reasoning_process_contracts import schema_metrics  # noqa: E402
from engine.system_b.reasoning_process_view_specific import (  # noqa: E402
    ROLE_FIELDS,
    VIEW_QUESTIONS,
    build_annotated_reader_packet,
    build_view_specific_prompts,
    compile_protected_fixture,
    protected_fixture_response,
    validate_annotated_reader_packet,
    view_specific_response_schema,
)
from engine.system_b.reasoning_process_views import (  # noqa: E402
    canonical_json_bytes,
    sha256_bytes,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verify_frozen_inputs(contract: dict[str, Any], root: Path) -> None:
    for item in contract["frozen_inputs"]:
        path = root / item["path"]
        if not path.is_file():
            raise ValueError(f"frozen input missing: {item['path']}")
        if _file_sha(path) != item["sha256"]:
            raise ValueError(f"frozen input drifted: {item['path']}")


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def build(*, root: Path, contract: dict[str, Any], output: Path) -> dict[str, Any]:
    _verify_frozen_inputs(contract, root)
    phase2_contract = _load(root / contract["phase2_contract_path"])
    expected_ids = contract["case_ids"]
    cases = phase2_contract["cases"]
    if [case["case_id"] for case in cases] != expected_ids:
        raise ValueError("Phase-2 case order or membership drifted")

    schema_artifacts: list[dict[str, Any]] = []
    for view_kind in VIEW_QUESTIONS:
        schema = view_specific_response_schema(view_kind)
        metrics = schema_metrics(schema)
        if metrics["bytes"] > contract["gates"]["max_provider_schema_bytes"]:
            raise ValueError(f"provider schema byte budget exceeded: {view_kind}")
        if metrics["depth"] > contract["gates"]["max_provider_schema_depth"]:
            raise ValueError(f"provider schema depth exceeded: {view_kind}")
        schema_path = output / "schemas" / f"{view_kind}.json"
        _write(schema_path, schema)
        schema_artifacts.append(
            {
                "view_kind": view_kind,
                "path": _relative(schema_path, root),
                "sha256": sha256_bytes(canonical_json_bytes(schema)),
                "metrics": metrics,
                "required_evidence_roles": list(ROLE_FIELDS[view_kind]),
                "free_form_source_quote_field_present": False,
            }
        )

    target_results: list[dict[str, Any]] = []
    packet_bytes: list[int] = []
    auxiliary_included = 0
    base_ledger_hashes: dict[str, str] = {}
    for case in cases:
        case_id = case["case_id"]
        source_path = root / case["source_path"]
        ledger_path = root / case["phase1_ledger_path"]
        source_text = source_path.read_text(encoding="utf-8")
        ledger = _load(ledger_path)
        before_hash = _file_sha(ledger_path)
        base_ledger_hashes[case_id] = before_hash
        catalog = build_source_catalog(
            source_text=source_text, source_path=case["source_path"]
        )
        for target in case["targets"]:
            view_kind = target["view_kind"]
            wrapper = build_annotated_reader_packet(
                case_id=case_id,
                view_kind=view_kind,
                question=VIEW_QUESTIONS[view_kind],
                source_path=case["source_path"],
                source_text=source_text,
                base_observations=ledger["observations"],
            )
            packet_validation = validate_annotated_reader_packet(
                wrapper, source_text=source_text
            )
            response = protected_fixture_response(
                target=target, wrapper=wrapper, catalog=catalog
            )
            compiled = compile_protected_fixture(
                target=target,
                response=response,
                wrapper=wrapper,
                base_ledger=ledger,
                catalog=catalog,
            )
            prompts = build_view_specific_prompts(wrapper)
            target_dir = output / "cases" / case_id / view_kind
            paths = {
                "reader_packet": target_dir / "reader-packet.json",
                "protected_fixture_response": target_dir
                / "protected-fixture-response.json",
                "compiled_fixture": target_dir / "compiled-fixture.json",
                "prompt_manifest": target_dir / "prompt-manifest.json",
            }
            _write(paths["reader_packet"], wrapper)
            _write(paths["protected_fixture_response"], response)
            _write(paths["compiled_fixture"], compiled)
            _write(
                paths["prompt_manifest"],
                {
                    "system_prompt_sha256": prompts["system_prompt_sha256"],
                    "user_prompt_sha256": prompts["user_prompt_sha256"],
                    "system_prompt": prompts["system_prompt"],
                    "target_blind": True,
                    "protected_target_present": False,
                    "provider_call_authorized": False,
                },
            )
            observed_bytes = wrapper["metrics"]["observed_input_utf8_bytes"]
            packet_bytes.append(observed_bytes)
            auxiliary_included += int(
                wrapper["reader_packet"]["auxiliary_phase1_ledger"]["included"]
            )
            target_results.append(
                {
                    "case_id": case_id,
                    "target_id": target["target_id"],
                    "view_kind": view_kind,
                    "status": compiled["status"],
                    "packet_validation": packet_validation,
                    "input_utf8_bytes": observed_bytes,
                    "source_sentence_count": wrapper["metrics"][
                        "source_sentence_count"
                    ],
                    "auxiliary_ledger_included": wrapper["reader_packet"][
                        "auxiliary_phase1_ledger"
                    ]["included"],
                    "source_content_complete": True,
                    "protected_target_in_packet": False,
                    "role_source_spans": compiled["view"]["items"][0][
                        "source_span_ids"
                    ],
                    "artifacts": {
                        name: _relative(path, root) for name, path in paths.items()
                    },
                }
            )
        if _file_sha(ledger_path) != before_hash:
            raise ValueError(f"Phase-1 ledger was modified: {case_id}")

    stress_spec = contract["stress_fixture"]
    stress_source_path = root / stress_spec["source_path"]
    stress_source = stress_source_path.read_text(encoding="utf-8")
    stress_observations = _load(root / stress_spec["auxiliary_path"])["observations"]
    stress_results: list[dict[str, Any]] = []
    for view_kind in VIEW_QUESTIONS:
        wrapper = build_annotated_reader_packet(
            case_id=stress_spec["case_id"],
            view_kind=view_kind,
            question=VIEW_QUESTIONS[view_kind],
            source_path=stress_spec["source_path"],
            source_text=stress_source,
            base_observations=stress_observations,
        )
        validation = validate_annotated_reader_packet(
            wrapper, source_text=stress_source
        )
        path = output / "stress" / f"{view_kind}.json"
        _write(path, wrapper)
        stress_results.append(
            {
                "view_kind": view_kind,
                "path": _relative(path, root),
                "validation": validation,
                "metrics": wrapper["metrics"],
            }
        )

    if len(target_results) != contract["expected"]["protected_target_count"]:
        raise ValueError("protected target count drifted")
    if len({item["view_kind"] for item in target_results}) != 5:
        raise ValueError("not all five semantic views were compiled")
    if any(item["status"] != "provider_free_view_specific_fixture_pass" for item in target_results):
        raise ValueError("a protected fixture failed")
    if any(not item["metrics"]["auxiliary_ledger_omitted_whole"] for item in stress_results):
        raise ValueError("stress fixture must omit the auxiliary ledger whole")

    return {
        "schema_version": "lolla.reasoning_process_view_specific_report.v1",
        "status": "provider_free_view_specific_interface_pass",
        "date": contract["date"],
        "contract_sha256": sha256_bytes(canonical_json_bytes(contract)),
        "implementation": {
            "module_path": "engine/system_b/reasoning_process_view_specific.py",
            "module_sha256": _file_sha(
                root / "engine/system_b/reasoning_process_view_specific.py"
            ),
            "builder_path": "scripts/evals/build_reasoning_process_view_specific_interface.py",
            "builder_sha256": _file_sha(
                root / "scripts/evals/build_reasoning_process_view_specific_interface.py"
            ),
        },
        "summary": {
            "case_count": len(cases),
            "protected_target_count": len(target_results),
            "view_kind_count": len(VIEW_QUESTIONS),
            "compiled_fixture_pass_count": sum(
                item["status"] == "provider_free_view_specific_fixture_pass"
                for item in target_results
            ),
            "current_packet_auxiliary_ledger_included_count": auxiliary_included,
            "current_packet_min_utf8_bytes": min(packet_bytes),
            "current_packet_max_utf8_bytes": max(packet_bytes),
            "stress_packet_count": len(stress_results),
            "stress_packet_max_utf8_bytes": max(
                item["metrics"]["observed_input_utf8_bytes"]
                for item in stress_results
            ),
            "stress_auxiliary_ledger_omitted_whole_count": sum(
                item["metrics"]["auxiliary_ledger_omitted_whole"]
                for item in stress_results
            ),
            "provider_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "schemas": schema_artifacts,
        "protected_fixtures": target_results,
        "stress_fixtures": stress_results,
        "base_ledger_file_sha256": base_ledger_hashes,
        "decision": {
            "provider_free_representation_gate": "pass",
            "semantic_model_behavior_validated": False,
            "next_step": "freeze a new one-case Gemini-via-OpenRouter development-probe contract before any call",
            "phase4_transfer_authorized": False,
        },
        "nonclaims": [
            "The source-reviewed protected fixtures are development scaffolding, not independent gold.",
            "A passing provider-free interface does not show that a model will populate it correctly.",
            "No final-output quality, trust, effort, or proof-of-work conclusion follows.",
            "No graph value or runtime readiness was tested.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path(
            "docs/evals/reasoning-process-view-specific-interface-contract-v1.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "research/reasoning-process-view-specific-interface-2026-07-11"
        ),
    )
    args = parser.parse_args()
    root = args.repo_root.resolve()
    contract = _load(root / args.contract)
    output = root / args.output
    report = build(root=root, contract=contract, output=output)
    _write(output / "report.json", report)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
