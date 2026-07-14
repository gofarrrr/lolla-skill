#!/usr/bin/env python3
"""Build provider-free Phase-2 coverage and bounded-view artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_views import (
    build_coverage_candidates,
    build_fan_in_stress_fixture,
    build_phase2_artifacts,
    canonical_json_bytes,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _report_path(path: Path, *, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path("docs/evals/reasoning-process-phase2-coverage-contract-v1.json"),
    )
    parser.add_argument("--review", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/reasoning-process-phase2-views-2026-07-11"),
    )
    args = parser.parse_args()
    root = args.repo_root.resolve()
    contract = json.loads((root / args.contract).read_text(encoding="utf-8"))
    candidates = build_coverage_candidates(contract=contract, repo_root=root)
    output = root / args.output
    _write_json(output / "coverage-candidates.json", candidates)
    if args.review is None:
        print(
            json.dumps(
                {
                    "status": "coverage_candidates_built_review_required",
                    "candidate_sha256": __import__("hashlib").sha256(
                        canonical_json_bytes(candidates)
                    ).hexdigest(),
                    "target_count": candidates["target_count"],
                    "output": str(output / "coverage-candidates.json"),
                },
                indent=2,
            )
        )
        return 0

    review = json.loads((root / args.review).read_text(encoding="utf-8"))
    result = build_phase2_artifacts(
        contract=contract,
        candidates=candidates,
        review=review,
        repo_root=root,
    )
    stress_source_path = Path("research/test-cases/case_parenting_teen_conversation.txt")
    stress_source = (root / stress_source_path).read_text(encoding="utf-8")
    stress = build_fan_in_stress_fixture(
        source_text=stress_source,
        source_path=str(stress_source_path),
        source_sha256="c8a8cfa4280cd2d359cdf89736c4c54e415c6a23ed24ac4ab01442b41edae3b4",
    )
    _write_json(output / "fan-in-stress-fixture.json", stress)
    result["fan_in_stress"] = {
        "status": stress["status"],
        "artifact_path": str(args.output / "fan-in-stress-fixture.json"),
        "source_message_count": stress["source_manifest"]["message_count"],
        "input_observation_count": stress["view"]["budget"]["observed_input_observations"],
        "input_utf8_bytes": stress["view"]["budget"]["observed_input_utf8_bytes"],
        "budget_exceeded": stress["view"]["budget"]["budget_exceeded"],
        "semantic_quality_evaluated": False,
        "probe_input_utf8_bytes": stress["probe_input"]["metrics"]["observed_input_utf8_bytes"],
        "probe_auxiliary_ledger_omitted_whole": stress["probe_input"]["metrics"]["auxiliary_ledger_omitted_whole"],
    }
    for case in result["cases"]:
        case_dir = output / "cases" / case["case_id"]
        _write_json(case_dir / "addendum.json", case.pop("addendum"))
        _write_json(case_dir / "combined-manifest.json", case.pop("combined_manifest"))
        views = case.pop("views")
        for view in views:
            _write_json(case_dir / "views" / f"{view['view_kind']}.json", view)
        probe_inputs = case.pop("probe_inputs")
        probe_artifacts = []
        for probe in probe_inputs:
            view_kind = probe["packet"]["view_kind"]
            probe_path = case_dir / "probe-inputs" / f"{view_kind}.json"
            _write_json(probe_path, probe)
            probe_artifacts.append(
                {
                    "view_kind": view_kind,
                    "path": _report_path(probe_path, root=root),
                    "canonical_sha256": hashlib.sha256(
                        canonical_json_bytes(probe)
                    ).hexdigest(),
                    "metrics": probe["metrics"],
                }
            )
        case["probe_input_artifacts"] = probe_artifacts
    _write_json(output / "report.json", result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "case_count": result["case_count"],
                "view_count": result["view_count"],
                "addendum_observation_count": result["addendum_observation_count"],
                "output": str(output / "report.json"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
