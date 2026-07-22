#!/usr/bin/env python3
"""Build or validate a provider-free graph-substrate candidate directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from system_b.compilation_bundle import GraphCompilationError, KnowledgeCompiler


def _summary(result, output_dir: Path) -> dict[str, object]:
    manifest = json.loads((output_dir / "compilation_manifest.json").read_text(encoding="utf-8"))
    comparison = manifest["published_comparison"]
    byte_equivalent = all(bool(item["byte_equivalent"]) for item in comparison.values())
    return {
        "status": "valid" if result.is_valid else "failed",
        "candidate_directory": str(output_dir),
        "model_count": result.bundle.model_count,
        "knowledge_edge_count": result.bundle.knowledge_edge_count,
        "relationship_edge_count": result.bundle.relationship_edge_count,
        "published_byte_equivalent": byte_equivalent,
        "published_overwrite_performed": manifest["published_overwrite_performed"],
        "provider_calls": 0,
        "errors": list(result.errors),
        "warnings": list(result.warnings),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = root / output_dir
    output_dir = output_dir.resolve()

    compiler = KnowledgeCompiler.load(root)
    result = (
        compiler.validate_candidate_directory(output_dir)
        if args.validate_only
        else compiler.compile(output_dir=output_dir)
    )
    summary = _summary(result, output_dir)
    if not result.is_valid:
        raise GraphCompilationError("Candidate validation failed: " + "; ".join(result.errors))
    if not summary["published_byte_equivalent"]:
        raise GraphCompilationError(
            "Current-release reconstruction differs from published graph bytes; inspect the candidate manifest"
        )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
