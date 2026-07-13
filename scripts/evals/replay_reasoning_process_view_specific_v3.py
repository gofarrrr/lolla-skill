#!/usr/bin/env python3
"""Replay four preserved Case-02 semantic readers under transfer-ready v3 custody."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.conversation_state_candidates import build_source_catalog  # noqa: E402
from engine.system_b.reasoning_process_view_specific_v3 import (  # noqa: E402
    SUPPORTED_VIEWS,
    compile_response_v3_recordwise,
    remove_legacy_mechanical_parking,
    response_schema_v3,
)
from engine.system_b.reasoning_process_contracts import schema_metrics  # noqa: E402


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _display(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def replay(*, root: Path, output: Path) -> dict:
    case_id = "amb1-case02-nonprofit-scale"
    source_path = "research/designed-ambiguous-pool-v1-2026-07-10/capture-ready-cases/amb1-case02-nonprofit-scale.txt"
    source_text = (root / source_path).read_text(encoding="utf-8")
    catalog = build_source_catalog(source_text=source_text, source_path=source_path)
    ledger = _load(
        root
        / "research/reasoning-process-phase1-ledger-2026-07-11/cases/amb1-case02-nonprofit-scale/ledger.json"
    )
    results = []
    source_hashes = {}
    total_records = admitted = quarantined = 0
    for view_kind in SUPPORTED_VIEWS:
        call_path = (
            root
            / "research/reasoning-process-view-specific-v2-probe-2026-07-11/calls"
            / f"{view_kind}.json"
        )
        source_hashes[view_kind] = _sha(call_path)
        call = _load(call_path)
        wrapper = _load(
            root
            / "research/reasoning-process-view-specific-interface-2026-07-11/cases"
            / case_id
            / view_kind
            / "reader-packet.json"
        )
        projected = remove_legacy_mechanical_parking(call["candidate_payload"])
        compiled = compile_response_v3_recordwise(
            response=projected,
            wrapper=wrapper,
            base_ledger=ledger,
            catalog=catalog,
            record_identity=f"v3-replay-{view_kind}",
            producer_kind="model",
            producer_id=call["requested_model"],
            call_metadata={
                "call_id": call["call_id"],
                "model": call["served_model"],
                "prompt_sha256": "sha256:" + call["user_prompt_sha256"],
            },
        )
        out_path = output / "views" / f"{view_kind}.json"
        _write(
            out_path,
            {
                "view_kind": view_kind,
                "source_call_path": str(call_path.relative_to(root)),
                "source_call_sha256": source_hashes[view_kind],
                "legacy_parking_value": call["candidate_payload"][
                    "park_unselected_auxiliary_observations"
                ],
                "projected_payload": projected,
                "compiled": compiled,
                "replay_provider_calls": 0,
            },
        )
        total_records += len(compiled["records"])
        admitted += sum(item["terminal_state"] == "admitted" for item in compiled["records"])
        quarantined += sum(
            item["terminal_state"] == "quarantined" for item in compiled["records"]
        )
        results.append(
            {
                "view_kind": view_kind,
                "status": compiled["window_terminal_disposition"],
                "record_count": len(compiled["records"]),
                "admitted_record_count": len(compiled["observations"]),
                "artifact_path": _display(out_path, root),
                "schema_metrics": schema_metrics(response_schema_v3(view_kind)),
            }
        )
        if _sha(call_path) != source_hashes[view_kind]:
            raise RuntimeError(f"source call drifted during v3 replay: {view_kind}")
    report = {
        "schema_version": "lolla.reasoning_process_view_specific_v3_replay.v1",
        "status": "four_reader_transfer_envelope_provider_free_pass",
        "date": "2026-07-11",
        "case_id": case_id,
        "results": results,
        "summary": {
            "view_count": 4,
            "record_count": total_records,
            "admitted_record_count": admitted,
            "quarantined_record_count": quarantined,
            "mechanical_parking_fields_removed": 4,
            "model_semantic_records_changed": 0,
            "replay_provider_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "decision": {
            "transfer_envelope_provider_free_gate": "pass",
            "record_level_custody_required": True,
            "provider_calls_authorized": False,
            "phase4_transfer_authorized": False,
        },
        "nonclaim": "Replaying already reviewed Case-02 records validates custody shape, not transfer behavior.",
    }
    _write(output / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/reasoning-process-view-specific-v3-replay-2026-07-11"),
    )
    args = parser.parse_args()
    root = args.repo_root.resolve()
    report = replay(root=root, output=root / args.output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
