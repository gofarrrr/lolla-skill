#!/usr/bin/env python3
"""Mechanically package all V1 conversations for two-call role interpretation."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.simulated_reliability_v1 import (
    build_position_wrapper,
    build_role_request_bundle,
)


MANIFEST = ROOT / "research/simulated-reliability-corpus-v1-2026-07-12/manifest.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    manifest = load(MANIFEST)
    artifacts = []
    for split_name, key in (("calibration", "calibration_cases"), ("transfer", "transfer_cases")):
        for item in manifest[key]:
            source = ROOT / item["path"]
            if sha(source) != item["sha256"]:
                raise RuntimeError(f"source hash drifted: {item['case_id']}")
            wrapper = build_position_wrapper(
                case_id=item["case_id"],
                conversation=source.read_text(encoding="utf-8"),
                source_path=item["path"],
                source_sha256=item["sha256"],
            )
            bundle = build_role_request_bundle(wrapper=wrapper)
            case_dir = output / split_name / item["case_id"]
            write(case_dir / "position-wrapper.json", wrapper)
            write(case_dir / "role-request-bundle.json", bundle)
            artifacts.append(
                {
                    "case_id": item["case_id"],
                    "split": split_name,
                    "source_path": item["path"],
                    "source_sha256": item["sha256"],
                    "message_count": wrapper["metrics"]["conversation_message_count"],
                    "evidence_alias_count": wrapper["metrics"]["focal_sentence_count"],
                    "annotated_input_utf8_bytes": wrapper["metrics"]["input_utf8_bytes"],
                    "wrapper_sha256": wrapper["wrapper_sha256"],
                    "request_bundle_sha256": bundle["bundle_sha256"],
                    "provider_calls": 0,
                }
            )
    external_controls = [
        {
            "case_id": "phase5-independent-quiet-library-laptop-pilot",
            "path": "research/independent-phase5-cases-2026-07-12/quiet-library-laptop-case.txt",
        }
    ]
    for item in external_controls:
        source = ROOT / item["path"]
        source_hash = sha(source)
        wrapper = build_position_wrapper(
            case_id=item["case_id"],
            conversation=source.read_text(encoding="utf-8"),
            source_path=item["path"],
            source_sha256=source_hash,
        )
        bundle = build_role_request_bundle(wrapper=wrapper)
        case_dir = output / "calibration_control" / item["case_id"]
        write(case_dir / "position-wrapper.json", wrapper)
        write(case_dir / "role-request-bundle.json", bundle)
        artifacts.append(
            {
                "case_id": item["case_id"],
                "split": "calibration_control",
                "source_path": item["path"],
                "source_sha256": source_hash,
                "message_count": wrapper["metrics"]["conversation_message_count"],
                "evidence_alias_count": wrapper["metrics"]["focal_sentence_count"],
                "annotated_input_utf8_bytes": wrapper["metrics"]["input_utf8_bytes"],
                "wrapper_sha256": wrapper["wrapper_sha256"],
                "request_bundle_sha256": bundle["bundle_sha256"],
                "provider_calls": 0,
            }
        )
    report = {
        "schema_version": "lolla.simulated_reliability_role_input_preflight.v1",
        "status": "provider_free_role_input_preflight_pass",
        "manifest_path": str(MANIFEST.relative_to(ROOT)),
        "manifest_sha256": sha(MANIFEST),
        "artifacts": artifacts,
        "summary": {
            "case_count": len(artifacts),
            "calibration_count": sum(item["split"] == "calibration" for item in artifacts),
            "transfer_count": sum(item["split"] == "transfer" for item in artifacts),
            "calibration_control_count": sum(item["split"] == "calibration_control" for item in artifacts),
            "minimum_message_count": min(item["message_count"] for item in artifacts),
            "maximum_message_count": max(item["message_count"] for item in artifacts),
            "maximum_evidence_alias_count": max(item["evidence_alias_count"] for item in artifacts),
            "maximum_annotated_input_utf8_bytes": max(item["annotated_input_utf8_bytes"] for item in artifacts),
            "maximum_provider_calls_per_case": 2,
            "provider_calls": 0,
        },
        "boundary": {
            "mechanical_full_source_projection_only": True,
            "semantic_prefilter": False,
            "transfer_outputs_used_for_tuning": False,
            "pipeline_provider_calls": 0,
        },
    }
    write(output / "report.json", report)
    print(json.dumps({"status": report["status"], "summary": report["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
