#!/usr/bin/env python3
"""Build deterministic blind three-arm review packets for Lolla V1."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ARMS = ("transcript_only", "direct_pressure", "graph_expanded_pressure")


class ReviewPacketError(ValueError):
    pass


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: Any) -> None:
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


def arm_output(result: dict[str, Any], arm_id: str) -> str:
    arm = result["arm_results"][arm_id]
    if arm.get("call_required") is False:
        output = arm.get("public_output")
    else:
        compiled = arm.get("compiled")
        if not isinstance(compiled, dict):
            raise ReviewPacketError(f"called arm lacks compiled output: {arm_id}")
        output = compiled.get("reconsidered_answer")
    if not isinstance(output, str) or not output.strip():
        raise ReviewPacketError(f"arm lacks public output: {arm_id}")
    return output


def build_packet(
    *,
    run_id: str,
    case_id: str,
    conversation: str,
    result: dict[str, Any],
    contract: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    if result.get("status") != "transfer_case_execution_complete_source_review_required":
        raise ReviewPacketError("case is not a complete transfer result")
    order = sorted(
        ARMS,
        key=lambda arm_id: hashlib.sha256(
            f"{run_id}|{case_id}|{arm_id}".encode("utf-8")
        ).hexdigest(),
    )
    labels = ("A", "B", "C")
    mapping = dict(zip(labels, order, strict=True))
    outputs = [
        {"blind_label": label, "public_output": arm_output(result, mapping[label])}
        for label in labels
    ]
    packet = {
        "schema_version": "lolla.simulated_reliability_blind_review_packet.v1",
        "run_id": run_id,
        "case_id": case_id,
        "authoritative_conversation": conversation,
        "outputs": outputs,
        "review_contract": contract,
        "boundaries": {
            "arm_identity_included": False,
            "source_review_disposition_included": False,
            "mental_model_candidates_included": False,
            "provider_telemetry_included": False,
            "scalar_score_requested": False,
        },
    }
    packet["packet_sha256"] = canonical_sha(packet)
    private = {
        "schema_version": "lolla.simulated_reliability_blind_mapping.v1",
        "run_id": run_id,
        "case_id": case_id,
        "packet_sha256": packet["packet_sha256"],
        "blind_label_to_arm_id": mapping,
        "stand_down": {
            arm_id: result["arm_results"][arm_id].get("call_required") is False
            for arm_id in ARMS
        },
    }
    private["mapping_sha256"] = canonical_sha(private)
    return packet, private


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transfer-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--review-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    args.transfer_root = args.transfer_root.resolve()
    args.manifest = args.manifest.resolve()
    args.review_contract = args.review_contract.resolve()
    args.output = args.output.resolve()

    manifest = load(args.manifest)
    contract = load(args.review_contract)
    if contract.get("schema_version") != "lolla.simulated_reliability_review_contract.v1":
        raise ReviewPacketError("review contract schema is invalid")
    if contract.get("scalar_quality_score_forbidden") is not True:
        raise ReviewPacketError("review contract permits a scalar score")

    source_by_id = {
        item["case_id"]: ROOT / item["path"] for item in manifest["transfer_cases"]
    }
    rows = []
    for result_path in sorted(args.transfer_root.glob("*-primary/result.json")):
        result = load(result_path)
        case_id = result.get("case_id")
        if result.get("status") != "transfer_case_execution_complete_source_review_required":
            rows.append(
                {
                    "result_path": str(result_path.relative_to(ROOT)),
                    "status": "excluded_incomplete",
                    "case_id": case_id,
                }
            )
            continue
        if case_id not in source_by_id:
            raise ReviewPacketError("complete case is absent from the manifest")
        source = source_by_id[case_id]
        packet, private = build_packet(
            run_id=args.run_id,
            case_id=case_id,
            conversation=source.read_text(encoding="utf-8"),
            result=result,
            contract=contract,
        )
        case_root = args.output / case_id
        write(case_root / "blind-review-packet.json", packet)
        write(case_root / "private-arm-mapping.json", private)
        rows.append(
            {
                "case_id": case_id,
                "status": "built",
                "packet_path": str((case_root / "blind-review-packet.json").relative_to(ROOT)),
                "packet_sha256": sha_bytes(case_root / "blind-review-packet.json"),
                "mapping_path": str((case_root / "private-arm-mapping.json").relative_to(ROOT)),
                "mapping_sha256": sha_bytes(case_root / "private-arm-mapping.json"),
            }
        )
    report = {
        "schema_version": "lolla.simulated_reliability_review_packet_build_report.v1",
        "status": "complete",
        "run_id": args.run_id,
        "review_contract_path": str(args.review_contract.relative_to(ROOT)),
        "review_contract_sha256": sha_bytes(args.review_contract),
        "built_count": sum(row["status"] == "built" for row in rows),
        "excluded_incomplete_count": sum(row["status"] == "excluded_incomplete" for row in rows),
        "cases": rows,
        "integrity_limit": contract["integrity_limit"],
    }
    write(args.output / "report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
