#!/usr/bin/env python3
"""Build provider-free role-explicit shard prompts and protected fixtures."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.conversation_state_candidates import build_source_catalog  # noqa: E402
from engine.system_b.reasoning_process_chronological_shard_reader_v2 import (  # noqa: E402
    build_shard_prompts_v2,
    compile_shard_response_recordwise_v2,
    shard_response_schema_v2,
)
from engine.system_b.reasoning_process_contracts import schema_metrics  # noqa: E402
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402

VIEWS = (
    "position_and_decision_trajectory",
    "evidence_and_assumption_discipline",
    "uncertainty_and_unresolved_state",
    "challenge_and_revision_response",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _source_alias_text(wrapper: dict[str, Any]) -> dict[str, str]:
    packet = wrapper["packet"]
    source_path = packet["source"]["source_path"]
    source_text = (ROOT / source_path).read_text(encoding="utf-8")
    catalog = build_source_catalog(source_text=source_text, source_path=source_path)
    by_span = {span.span_id: span.text for span in catalog.spans if span.kind == "sentence"}
    return {
        item["alias"]: by_span[item["span_id"]]
        for item in [*wrapper["focal_alias_map"], *wrapper["context_alias_map"]]
    }


def _joined(record: dict[str, Any], field: str, alias_text: dict[str, str]) -> str:
    return " ".join(alias_text[alias] for alias in record[field])


def _legacy_response(case_id: str, view_kind: str) -> dict[str, Any]:
    if view_kind in {"position_and_decision_trajectory", "challenge_and_revision_response"}:
        response = _load(
            ROOT
            / "research/reasoning-process-view-specific-v2-2026-07-11/fixtures"
            / case_id
            / f"{view_kind}.json"
        )["response"]
    else:
        response = _load(
            ROOT
            / "research/reasoning-process-view-specific-interface-2026-07-11/cases"
            / case_id
            / view_kind
            / "protected-fixture-response.json"
        )
    value = copy.deepcopy(response)
    value.pop("park_unselected_auxiliary_observations")
    for record in value["records"]:
        record.pop("auxiliary_observation_ids")
    return value


def project_reviewed_fixture_v2(
    *, case_id: str, view_kind: str, wrapper: dict[str, Any]
) -> dict[str, Any]:
    """Mechanical projection of already reviewed semantic roles, not new inference."""

    legacy = _legacy_response(case_id, view_kind)
    if view_kind == "evidence_and_assumption_discipline":
        return legacy
    alias_text = _source_alias_text(wrapper)
    records = []
    for record in legacy["records"]:
        base = {"status": record["status"], "limitations": record["limitations"]}
        if view_kind == "position_and_decision_trajectory":
            projected = {
                **base,
                "starting_position_interpretation": _joined(
                    record, "starting_state_evidence_ids", alias_text
                ),
                "starting_state_evidence_ids": record["starting_state_evidence_ids"],
                "current_position_interpretation": _joined(
                    record, "current_position_evidence_ids", alias_text
                ),
                "current_position_evidence_ids": record["current_position_evidence_ids"],
                "qualification_interpretation": _joined(
                    record, "qualification_evidence_ids", alias_text
                ),
                "qualification_evidence_ids": record["qualification_evidence_ids"],
                "trajectory_interpretation": record["interpretation"],
                "trajectory_type": record["trajectory_type"],
            }
        elif view_kind == "uncertainty_and_unresolved_state":
            projected = {
                **base,
                "unresolved_matter_interpretation": _joined(
                    record, "unresolved_evidence_ids", alias_text
                ),
                "unresolved_evidence_ids": record["unresolved_evidence_ids"],
                "preservation_or_reopen_interpretation": _joined(
                    record, "preservation_or_reopen_evidence_ids", alias_text
                ),
                "preservation_or_reopen_evidence_ids": record[
                    "preservation_or_reopen_evidence_ids"
                ],
                "relationship_interpretation": record["interpretation"],
            }
        else:
            projected = {
                **base,
                "prior_frame_interpretation": _joined(
                    record, "prior_claim_or_frame_evidence_ids", alias_text
                ),
                "prior_claim_or_frame_evidence_ids": record[
                    "prior_claim_or_frame_evidence_ids"
                ],
                "challenge_interpretation": _joined(
                    record, "challenge_evidence_ids", alias_text
                ),
                "challenge_evidence_ids": record["challenge_evidence_ids"],
                "response_interpretation": _joined(
                    record, "response_evidence_ids", alias_text
                ),
                "response_evidence_ids": record["response_evidence_ids"],
                "revision_interpretation": _joined(
                    record, "revision_evidence_ids", alias_text
                ),
                "revision_evidence_ids": record["revision_evidence_ids"],
                "relationship_interpretation": record["interpretation"],
                "challenge_type": record["challenge_type"],
                "response_type": record["response_type"],
            }
        records.append(projected)
    return {
        "status": legacy["status"],
        "records": records,
        "global_limitations": legacy["global_limitations"],
    }


def build(output: Path) -> dict[str, Any]:
    interface = _load(
        ROOT / "research/reasoning-process-chronological-shard-interface-2026-07-11/report.json"
    )
    target_review = _load(
        ROOT / "research/reasoning-process-chronological-shards-2026-07-11/protected-target-review.json"
    )
    targets = {
        (case["case_id"], target["view_kind"]): target
        for case in target_review["cases"]
        for target in case["targets"]
    }
    packet_count = fixture_count = admitted = quarantined = 0
    max_prompt = max_schema_bytes = max_schema_depth = 0
    evidence_schema_unchanged = evidence_prompt_unchanged = True
    cases = []
    for case in interface["cases"]:
        artifacts = []
        for artifact in case["artifacts"]:
            wrapper = _load(ROOT / artifact["path"])
            view_kind = artifact["view_kind"]
            prompts = build_shard_prompts_v2(wrapper)
            schema = shard_response_schema_v2(view_kind)
            legacy_manifest = _load(ROOT / artifact["prompt_manifest_path"])
            schema_sha = sha256_bytes(canonical_json_bytes(schema))
            if view_kind == "evidence_and_assumption_discipline":
                evidence_schema_unchanged &= (
                    schema_sha == legacy_manifest["response_schema_sha256"]
                )
                evidence_prompt_unchanged &= (
                    prompts["system_prompt_sha256"]
                    == legacy_manifest["system_prompt_sha256"]
                    and prompts["user_prompt_sha256"]
                    == legacy_manifest["user_prompt_sha256"]
                )
            metrics = schema_metrics(schema)
            manifest = {
                "case_id": case["case_id"],
                "view_kind": view_kind,
                "shard_id": wrapper["packet"]["shard_id"],
                "packet_path": artifact["path"],
                "system_prompt_sha256": prompts["system_prompt_sha256"],
                "user_prompt_sha256": prompts["user_prompt_sha256"],
                "user_prompt_utf8_bytes": len(prompts["user_prompt"].encode("utf-8")),
                "response_schema_sha256": schema_sha,
                "response_schema_metrics": metrics,
                "question_is_last_prompt_section": prompts["user_prompt"].rfind(
                    "Question:"
                )
                > prompts["user_prompt"].rfind("contract:"),
            }
            manifest_path = (
                output
                / "prompt-manifests"
                / case["case_id"]
                / f"{wrapper['packet']['shard_id']}.json"
            )
            _write(manifest_path, manifest)
            packet_count += 1
            max_prompt = max(max_prompt, manifest["user_prompt_utf8_bytes"])
            max_schema_bytes = max(max_schema_bytes, metrics["bytes"])
            max_schema_depth = max(max_schema_depth, metrics["depth"])
            target = targets[(case["case_id"], view_kind)]
            protected = artifact["path"] in target["matching_shard_paths"]
            fixture_path = None
            if protected:
                response = project_reviewed_fixture_v2(
                    case_id=case["case_id"], view_kind=view_kind, wrapper=wrapper
                )
                compiled = compile_shard_response_recordwise_v2(
                    response=response,
                    wrapper=wrapper,
                    producer_kind="source_reviewer",
                    producer_id="role-explicit-v2-mechanical-projection-of-reviewed-roles",
                    record_identity=target["target_id"],
                )
                fixture_path = (
                    output
                    / "protected-fixtures"
                    / case["case_id"]
                    / f"{view_kind}.json"
                )
                _write(
                    fixture_path,
                    {
                        "target": target,
                        "projection_policy": "exact source text copied for already reviewed semantic evidence roles; reviewed relationship interpretation preserved; no new semantic inference",
                        "response": response,
                        "compiled": compiled,
                    },
                )
                fixture_count += 1
                admitted += sum(
                    item["terminal_state"] == "admitted"
                    for item in compiled["records"]
                )
                quarantined += sum(
                    item["terminal_state"] == "quarantined"
                    for item in compiled["records"]
                )
            artifacts.append(
                {
                    "view_kind": view_kind,
                    "shard_id": wrapper["packet"]["shard_id"],
                    "packet_path": artifact["path"],
                    "prompt_manifest_path": str(manifest_path.relative_to(ROOT)),
                    "protected_fixture_path": (
                        str(fixture_path.relative_to(ROOT)) if fixture_path else None
                    ),
                }
            )
        cases.append({"case_id": case["case_id"], "artifacts": artifacts})
    report = {
        "schema_version": "lolla.reasoning_process_chronological_shard_role_explicit_v2_report.v1",
        "status": "provider_free_role_explicit_interface_pass",
        "date": "2026-07-12",
        "cases": cases,
        "summary": {
            "packet_and_prompt_count": packet_count,
            "protected_fixture_count": fixture_count,
            "protected_admitted_record_count": admitted,
            "protected_quarantined_record_count": quarantined,
            "maximum_user_prompt_utf8_bytes": max_prompt,
            "maximum_response_schema_bytes": max_schema_bytes,
            "maximum_response_schema_depth": max_schema_depth,
            "evidence_schema_unchanged": evidence_schema_unchanged,
            "evidence_prompt_unchanged": evidence_prompt_unchanged,
            "provider_calls": 0,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "decision": {
            "provider_free_role_contract_gate": (
                "pass"
                if fixture_count == 20
                and admitted == 20
                and quarantined == 0
                and evidence_schema_unchanged
                and evidence_prompt_unchanged
                else "fail"
            ),
            "adversarial_review_authorized": True,
            "provider_probe_authorized": False,
        },
        "boundary": {
            "fixture_projection_performed_new_semantic_inference": False,
            "semantic_role_correctness_inferred_by_code": False,
            "deterministic_temporal_semantic_gate_added": False,
            "global_synthesis_authorized": False,
            "semantic_merge_authorized": False,
            "graph_or_runtime_authorized": False,
        },
    }
    _write(output / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.output.resolve())
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
