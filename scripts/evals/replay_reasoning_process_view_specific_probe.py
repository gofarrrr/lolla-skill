#!/usr/bin/env python3
"""Replay preserved view-specific probe responses after a compiler-only fix."""
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

from engine.system_b.conversation_state_candidates import build_source_catalog  # noqa: E402
from engine.system_b.reasoning_process_view_specific import (  # noqa: E402
    validate_view_specific_response,
)
from engine.system_b.reasoning_process_view_specific_replay import (  # noqa: E402
    compile_preserved_model_response,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def replay(*, root: Path, probe_dir: Path, output_dir: Path) -> dict[str, Any]:
    contract = _load(
        root / "docs/evals/reasoning-process-view-specific-probe-contract-v1.json"
    )
    source_text = (root / contract["case"]["source_path"]).read_text(encoding="utf-8")
    catalog = build_source_catalog(
        source_text=source_text, source_path=contract["case"]["source_path"]
    )
    ledger_path = root / contract["case"]["phase1_ledger_path"]
    ledger_sha_before = _sha(ledger_path)
    ledger = _load(ledger_path)
    results: list[dict[str, Any]] = []
    for job in contract["jobs"]:
        view_kind = job["view_kind"]
        call_path = probe_dir / "calls" / f"{view_kind}.json"
        call_sha_before = _sha(call_path)
        call = _load(call_path)
        wrapper = _load(root / job["packet_path"])
        payload = call.get("candidate_payload")
        if not isinstance(payload, dict):
            results.append(
                {
                    "view_kind": view_kind,
                    "status": "no_preserved_payload",
                    "call_path": _display_path(call_path, root),
                    "call_sha256": call_sha_before,
                }
            )
            continue
        validate_view_specific_response(payload, wrapper=wrapper)
        compiled = compile_preserved_model_response(
            response=payload,
            wrapper=wrapper,
            base_ledger=ledger,
            catalog=catalog,
            call_metadata={
                "call_id": call["call_id"],
                "requested_model": call["requested_model"],
                "served_model": call["served_model"],
                "prompt_sha256": "sha256:" + call["user_prompt_sha256"],
            },
        )
        compiled_path = output_dir / "compiled" / f"{view_kind}.json"
        _write(compiled_path, compiled)
        if _sha(call_path) != call_sha_before:
            raise RuntimeError(f"preserved call changed during replay: {view_kind}")
        results.append(
            {
                "view_kind": view_kind,
                "status": compiled["status"],
                "call_path": _display_path(call_path, root),
                "call_sha256": call_sha_before,
                "compiled_path": _display_path(compiled_path, root),
                "compiled_sha256": _sha(compiled_path),
                "response_changed": compiled["response_changed"],
                "provider_calls": 0,
                "view_item_count": len(compiled["view"]["items"]),
            }
        )
    if _sha(ledger_path) != ledger_sha_before:
        raise RuntimeError("Phase-1 ledger changed during replay")
    report = {
        "schema_version": "lolla.reasoning_process_view_specific_replay_report.v1",
        "status": (
            "compiler_only_replay_complete"
            if len(results) == 5
            and all(item["status"] == "preserved_model_response_compiled" for item in results)
            else "compiler_only_replay_incomplete"
        ),
        "run_id": contract["run_id"],
        "failure_classification": "local_compiler_authority_vocabulary_mismatch",
        "repair_scope": "deterministic replay of unchanged preserved payloads",
        "results": results,
        "summary": {
            "preserved_payload_count": sum(
                item["status"] == "preserved_model_response_compiled" for item in results
            ),
            "typed_and_compiled_count_after_replay": sum(
                item["status"] == "preserved_model_response_compiled" for item in results
            ),
            "response_change_count": sum(bool(item.get("response_changed")) for item in results),
            "provider_calls": 0,
            "embedding_calls": 0,
            "evaluator_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "phase1_ledger_path": str(ledger_path.relative_to(root)),
        "phase1_ledger_sha256_before_and_after": ledger_sha_before,
        "semantic_review_status": "still_required",
        "nonclaim": "Compiler admission does not establish semantic adequacy or protected-target visibility.",
    }
    _write(output_dir / "replay-report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--probe-dir",
        type=Path,
        default=Path("research/reasoning-process-view-specific-probe-2026-07-11"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/reasoning-process-view-specific-replay-2026-07-11"),
    )
    args = parser.parse_args()
    root = args.repo_root.resolve()
    report = replay(
        root=root, probe_dir=root / args.probe_dir, output_dir=root / args.output
    )
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
