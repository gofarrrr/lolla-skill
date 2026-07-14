#!/usr/bin/env python3
"""Build self-contained JSON and Markdown receipts for Lolla V1 case attempts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


class ReceiptError(ValueError):
    pass


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def case_id_from_dir(case_dir: Path) -> str:
    value = case_dir.name
    for suffix in ("-primary", "-repeat_2", "-repeat_3"):
        if value.endswith(suffix):
            return value[: -len(suffix)]
    raise ReceiptError("case directory lacks a recognized repeat suffix")


def final_assistant(conversation: str) -> str:
    values = re.findall(
        r"(?ms)^\[Turn \d+\] ASSISTANT:\n(.*?)(?=^\[Turn \d+\] (?:USER|ASSISTANT):\n|\Z)",
        conversation,
    )
    if not values:
        raise ReceiptError("conversation lacks an assistant contribution")
    return values[-1].strip()


def call_summary(path: Path) -> dict[str, Any]:
    call = load(path)
    return {
        "artifact_path": str(path.relative_to(ROOT)),
        "artifact_sha256": sha_bytes(path),
        "task_id": call.get("task_id"),
        "operational_status": call.get("operational_status"),
        "provider_calls": call.get("provider_calls", 0),
        "requested_model": call.get("requested_model"),
        "served_model": call.get("served_model"),
        "served_provider": call.get("served_provider"),
        "wire_mode": call.get("wire_mode"),
        "reasoning_effort": call.get("reasoning_effort"),
        "usage": call.get("usage"),
        "provider_reported_cost_usd": call.get("provider_reported_cost_usd"),
        "duration_seconds": call.get("duration_seconds"),
        "validation_error": call.get("validation_error") or None,
        "provider_error": call.get("provider_error") or None,
        "request_body_sha256": call.get("request_body_sha256"),
        "raw_content_sha256": call.get("raw_content_sha256"),
        "compiled": call.get("compiled"),
    }


def optional_artifact(case_dir: Path, name: str) -> dict[str, Any] | None:
    path = case_dir / name
    if not path.exists():
        return None
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha_bytes(path),
        "content": load(path),
    }


def build_receipt(
    *, case_dir: Path, case_id: str, source_path: Path, contract_path: Path
) -> dict[str, Any]:
    result_path = case_dir / "result.json"
    if not result_path.exists():
        raise ReceiptError("case attempt lacks result.json")
    result = load(result_path)
    conversation = source_path.read_text(encoding="utf-8")
    calls = [call_summary(path) for path in sorted(case_dir.glob("call-*-result.json"))]
    role_calls = [call for call in calls if call["task_id"] in {"starting", "current_qualification"}]
    mechanism_call = next((call for call in calls if call["task_id"] == "mechanism"), None)
    arm_calls = {
        call["task_id"]: call
        for call in calls
        if call["task_id"] in {"transcript_only", "direct_pressure", "graph_expanded_pressure"}
    }
    artifacts = {
        name: optional_artifact(case_dir, filename)
        for name, filename in (
            ("joined_role_records", "joined-role-records.json"),
            ("mechanism_request", "mechanism-request.json"),
            ("direct_ledger", "direct-ledger.json"),
            ("graph_ledger", "graph-ledger.json"),
            ("three_arm_bundle", "three-arm-bundle.json"),
        )
    }
    failures = [
        {
            "task_id": call["task_id"],
            "operational_status": call["operational_status"],
            "validation_error": call["validation_error"],
            "provider_error": call["provider_error"],
            "artifact_path": call["artifact_path"],
        }
        for call in calls
        if call["operational_status"] != "ok"
    ]
    if result.get("join_error"):
        failures.append(
            {
                "task_id": "role_join",
                "operational_status": "local_validation_failed",
                "validation_error": result["join_error"],
                "provider_error": None,
                "artifact_path": str(result_path.relative_to(ROOT)),
            }
        )
    arm_public_outputs: dict[str, Any] = {}
    bundle = artifacts["three_arm_bundle"]
    if bundle:
        for arm_id, arm in bundle["content"]["arms"].items():
            call = arm_calls.get(arm_id)
            compiled = call.get("compiled") if call else None
            arm_public_outputs[arm_id] = {
                "call_required": arm.get("call_required"),
                "provider_attempted": bool(call),
                "operational_status": call.get("operational_status") if call else "deterministic_stand_down",
                "public_output": (
                    compiled.get("reconsidered_answer")
                    if isinstance(compiled, dict)
                    else arm.get("public_output")
                ),
                "change_summary": compiled.get("change_summary") if isinstance(compiled, dict) else None,
                "candidate_dispositions": (
                    compiled.get("candidate_dispositions", []) if isinstance(compiled, dict) else []
                ),
            }
    receipt = {
        "schema_version": "lolla.simulated_reliability_case_receipt.v1",
        "case_id": case_id,
        "attempt_status": result.get("status"),
        "repeat_id": "primary",
        "source": {
            "path": str(source_path.relative_to(ROOT)),
            "sha256": sha_bytes(source_path),
            "authoritative_conversation": conversation,
            "original_final_assistant_answer": final_assistant(conversation),
        },
        "runtime_contract": {
            "path": str(contract_path.relative_to(ROOT)),
            "sha256": sha_bytes(contract_path),
        },
        "interpretation": {
            "role_calls": role_calls,
            "joined_role_records": (
                artifacts["joined_role_records"]["content"]
                if artifacts["joined_role_records"]
                else None
            ),
            "mechanism_call": mechanism_call,
            "mechanism_assessments": (
                mechanism_call["compiled"].get("pattern_hypotheses", [])
                if mechanism_call and isinstance(mechanism_call.get("compiled"), dict)
                else []
            ),
            "routing_projection": (
                mechanism_call["compiled"].get("routing_projection")
                if mechanism_call and isinstance(mechanism_call.get("compiled"), dict)
                else None
            ),
        },
        "deterministic_pressure": {
            "direct_ledger": artifacts["direct_ledger"],
            "graph_ledger": artifacts["graph_ledger"],
            "semantic_relevance_gate_performed_by_code": False,
        },
        "public_arms": arm_public_outputs,
        "call_custody": calls,
        "failures": failures,
        "usage": {
            "provider_attempts": sum(int(call["provider_calls"] or 0) for call in calls),
            "successful_calls": sum(call["operational_status"] == "ok" for call in calls),
            "provider_reported_cost_usd": round(
                sum(float(call["provider_reported_cost_usd"] or 0) for call in calls), 12
            ),
            "automatic_retries": 0,
            "response_healing": False,
            "fallback_models": 0,
        },
        "reading_guide": [
            "The conversation is authoritative; interpretations are probabilistic and source-linked.",
            "User-process status and vanilla-answer coverage are separate; answer coverage is not user adoption.",
            "Deterministic recall preserves controlled identities and graph custody but does not prove applicability.",
            "Apply, reject, park, and stand-down outcomes are hypotheses, not proof of reasoning quality.",
            "A polished or changed public answer is not automatically better.",
            "Failures and missing stages are part of the receipt rather than silently repaired.",
        ],
        "non_claims": [
            "not_reasoning_quality_proof",
            "not_decision_correctness_proof",
            "not_human_usefulness_evidence",
            "not_a_trust_score_or_badge",
            "not_production_authorization",
        ],
    }
    receipt["receipt_sha256"] = canonical_sha(receipt)
    return receipt


def markdown(receipt: dict[str, Any]) -> str:
    lines = [
        f"# Lolla V1 reasoning receipt — {receipt['case_id']}",
        "",
        f"Status: `{receipt['attempt_status']}`  ",
        f"Receipt SHA-256: `{receipt['receipt_sha256']}`",
        "",
        "## How to read this receipt",
        "",
    ]
    lines.extend(f"- {item}" for item in receipt["reading_guide"])
    lines.extend(["", "## Authoritative conversation", "", receipt["source"]["authoritative_conversation"], ""])
    lines.extend(["## Probabilistic interpretation", ""])
    joined = receipt["interpretation"]["joined_role_records"]
    if joined:
        for role in ("starting", "current", "qualification"):
            records = joined.get("role_observations", {}).get(role, [])
            lines.append(f"### {role.title()}")
            lines.append("")
            if not records:
                lines.append("No admitted record.")
            for record in records:
                lines.append(f"- **Interpretation:** {record.get('role_interpretation', '')}")
                lines.append(f"- **Limitations:** {record.get('limitations', '')}")
                lines.append(f"- **Evidence IDs:** {', '.join(record.get('evidence_ids', [])) or 'none'}")
            lines.append("")
    else:
        lines.extend(["No joined role record was produced.", ""])
    lines.extend(["### Controlled mechanism assessments", ""])
    assessments = receipt["interpretation"]["mechanism_assessments"]
    if not assessments:
        lines.extend(["No compiled mechanism assessment was produced.", ""])
    else:
        lines.extend(
            f"- `{item['mechanism_id']}` — user `{item['user_process_status']}`, answer `{item['vanilla_answer_coverage']}`, routing `{item['routing_disposition']}`"
            for item in assessments
        )
        lines.append("")
    lines.extend(["## Deterministic pressure custody", ""])
    direct = receipt["deterministic_pressure"]["direct_ledger"]
    graph = receipt["deterministic_pressure"]["graph_ledger"]
    if not direct:
        lines.append("No direct or graph ledger was produced.")
    else:
        lines.append(
            f"Direct active candidates: {len(direct['content'].get('active_candidates', []))}; reserve: {len(direct['content'].get('reserve_candidates', []))}."
        )
        lines.append(
            f"Graph additions: {len(graph['content'].get('active_candidates', [])) if graph else 0}; graph reserve: {len(graph['content'].get('reserve_candidates', [])) if graph else 0}."
        )
    lines.extend(["", "## Public arms", ""])
    if not receipt["public_arms"]:
        lines.append("No public arm bundle was produced.")
    for arm_id, arm in receipt["public_arms"].items():
        lines.extend(
            [
                f"### {arm_id}",
                "",
                f"Call required: `{arm['call_required']}`; status: `{arm['operational_status']}`.",
                "",
                arm["public_output"] or "No public output.",
                "",
            ]
        )
    lines.extend(["## Failures", ""])
    if not receipt["failures"]:
        lines.append("No recorded operational or local-validation failure.")
    else:
        for failure in receipt["failures"]:
            detail = failure.get("validation_error") or failure.get("provider_error") or "no further detail"
            lines.append(f"- `{failure['task_id']}` / `{failure['operational_status']}` — {detail}")
    lines.extend(["", "## Usage", ""])
    usage = receipt["usage"]
    lines.extend(
        [
            f"- Provider attempts: {usage['provider_attempts']}",
            f"- Successful calls: {usage['successful_calls']}",
            f"- Provider-reported cost: ${usage['provider_reported_cost_usd']:.6f}",
            "- Automatic retries: 0",
            "- Response healing: false",
            "",
            "## Non-claims",
            "",
        ]
    )
    lines.extend(f"- `{item}`" for item in receipt["non_claims"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transfer-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--runtime-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.transfer_root = args.transfer_root.resolve()
    args.manifest = args.manifest.resolve()
    args.runtime_contract = args.runtime_contract.resolve()
    args.output = args.output.resolve()

    manifest = load(args.manifest)
    source_by_id = {item["case_id"]: ROOT / item["path"] for item in manifest["transfer_cases"]}
    rows = []
    for case_dir in sorted(path for path in args.transfer_root.glob("*-primary") if path.is_dir()):
        case_id = case_id_from_dir(case_dir)
        if case_id not in source_by_id:
            raise ReceiptError("attempt case is absent from manifest")
        receipt = build_receipt(
            case_dir=case_dir,
            case_id=case_id,
            source_path=source_by_id[case_id],
            contract_path=args.runtime_contract,
        )
        case_output = args.output / case_id
        json_path = case_output / "receipt.json"
        md_path = case_output / "receipt.md"
        write_json(json_path, receipt)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(markdown(receipt), encoding="utf-8")
        rows.append(
            {
                "case_id": case_id,
                "attempt_status": receipt["attempt_status"],
                "receipt_path": str(json_path.relative_to(ROOT)),
                "receipt_file_sha256": sha_bytes(json_path),
                "markdown_path": str(md_path.relative_to(ROOT)),
                "markdown_sha256": sha_bytes(md_path),
            }
        )
    report = {
        "schema_version": "lolla.simulated_reliability_receipt_build_report.v1",
        "status": "complete",
        "receipt_count": len(rows),
        "cases": rows,
        "non_claim": "receipt_build_success_is_not_cold_reader_success",
    }
    write_json(args.output / "report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
