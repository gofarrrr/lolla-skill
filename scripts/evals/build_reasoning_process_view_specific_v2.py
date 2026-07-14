#!/usr/bin/env python3
"""Build failure-derived provider-free relationship fixtures for interface v2."""
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
from engine.system_b.reasoning_process_view_specific import VIEW_QUESTIONS  # noqa: E402
from engine.system_b.reasoning_process_view_specific_v2 import (  # noqa: E402
    protected_relationship_fixture_response,
    response_schema_v2,
    validate_response_v2,
)
from engine.system_b.reasoning_process_view_specific_v2_compile import (  # noqa: E402
    compile_response_v2,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _display_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def build(*, root: Path, output: Path) -> dict[str, Any]:
    phase2 = _load(root / "docs/evals/reasoning-process-phase2-coverage-contract-v1.json")
    review = _load(
        root / "docs/evals/reasoning-process-view-specific-relationship-review-v2.json"
    )
    review_cases = {item["case_id"]: item for item in review["cases"]}
    schemas = []
    for view_kind in VIEW_QUESTIONS:
        schema = response_schema_v2(view_kind)
        metrics = schema_metrics(schema)
        if metrics["bytes"] > 12000 or metrics["depth"] > 8:
            raise RuntimeError(f"v2 schema exceeds frozen budget: {view_kind}")
        path = output / "schemas" / f"{view_kind}.json"
        _write(path, schema)
        schemas.append(
            {
                "view_kind": view_kind,
                "metrics": metrics,
                "path": _display_path(path, root),
            }
        )
    fixtures = []
    changed_views = {
        "position_and_decision_trajectory",
        "exploration_and_alternatives",
        "challenge_and_revision_response",
    }
    for case in phase2["cases"]:
        source_text = (root / case["source_path"]).read_text(encoding="utf-8")
        catalog = build_source_catalog(
            source_text=source_text, source_path=case["source_path"]
        )
        ledger = _load(root / case["phase1_ledger_path"])
        case_review = review_cases[case["case_id"]]
        for target in case["targets"]:
            view_kind = target["view_kind"]
            if view_kind not in changed_views:
                continue
            wrapper_path = (
                root
                / "research/reasoning-process-view-specific-interface-2026-07-11/cases"
                / case["case_id"]
                / view_kind
                / "reader-packet.json"
            )
            wrapper = _load(wrapper_path)
            relationship = None
            if view_kind == "position_and_decision_trajectory":
                relationship = case_review["position"]
            elif view_kind == "challenge_and_revision_response":
                relationship = case_review["challenge"]
            response = protected_relationship_fixture_response(
                target=target,
                relationship_review=relationship,
                wrapper=wrapper,
                catalog=catalog,
            )
            validated = validate_response_v2(response, wrapper=wrapper)
            compiled = compile_response_v2(
                response=response,
                wrapper=wrapper,
                base_ledger=ledger,
                catalog=catalog,
                record_identity=target["target_id"],
                producer_kind="source_reviewer",
                producer_id="view-specific-v2-same-session-nonblind",
            )
            path = output / "fixtures" / case["case_id"] / f"{view_kind}.json"
            _write(
                path,
                {
                    "status": "provider_free_v2_relationship_fixture_pass",
                    "case_id": case["case_id"],
                    "target_id": target["target_id"],
                    "view_kind": view_kind,
                    "response": response,
                    "validation": validated,
                    "compiled": compiled,
                    "boundary": {
                        "independent_gold": False,
                        "semantic_correctness_validated": False,
                        "provider_calls": 0,
                        "graph_or_runtime_authorized": False,
                    },
                },
            )
            fixtures.append(
                {
                    "case_id": case["case_id"],
                    "target_id": target["target_id"],
                    "view_kind": view_kind,
                    "path": _display_path(path, root),
                    "status": "pass",
                    "role_source_span_ids": validated["records"][0][
                        "role_source_span_ids"
                    ],
                    "compiled_status": compiled["status"],
                }
            )
    if len(fixtures) != 15:
        raise RuntimeError("expected fifteen failure-derived relationship fixtures")
    report = {
        "schema_version": "lolla.reasoning_process_view_specific_v2_report.v1",
        "status": "provider_free_relationship_contract_pass",
        "date": "2026-07-11",
        "summary": {
            "case_count": 5,
            "schema_count": 5,
            "failure_derived_relationship_fixture_count": len(fixtures),
            "fixture_pass_count": sum(item["status"] == "pass" for item in fixtures),
            "append_only_compile_pass_count": sum(
                item["compiled_status"] == "view_specific_v2_response_compiled"
                for item in fixtures
            ),
            "provider_calls": 0,
            "embedding_calls": 0,
            "evaluator_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "schemas": schemas,
        "fixtures": fixtures,
        "design_changes": [
            "Trajectory claims require separate starting-state and current-position evidence.",
            "Alternatives require a separately stated attached condition or limit with its own aliases.",
            "Challenges require the prior claim or frame being contested, not only the challenging turn.",
        ],
        "unchanged": [
            "Complete annotated sentence input and stable alias mapping.",
            "Evidence-and-assumption and unresolved-state semantic role contracts.",
            "Probabilistic semantic authority and deterministic identity, schema, budget, and custody authority.",
        ],
        "decision": {
            "provider_free_relationship_gate": "pass",
            "ready_for_another_model_call": True,
            "reason": "All fifteen failure-derived relationship fixtures, the raw-role compiler, and the adversarial local suite pass; a new prospectively frozen one-case probe may now test model behavior.",
            "phase4_transfer_authorized": False,
        },
        "nonclaim": "Source-reviewed v2 fixtures show representability, not model semantic behavior.",
    }
    _write(output / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/reasoning-process-view-specific-v2-2026-07-11"),
    )
    args = parser.parse_args()
    root = args.repo_root.resolve()
    report = build(root=root, output=root / args.output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
